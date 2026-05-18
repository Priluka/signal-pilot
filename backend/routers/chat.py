"""Chat answer endpoint — Server-Sent Events stream.

Architecture: generation runs in a **daemon thread** that writes chunks to
the ``chat_sessions`` row as they arrive. The HTTP response is a thin SSE
tail that polls the row and emits events to the client. If the client
disconnects (refresh, navigation, broken network), the generator thread
keeps going to completion — the answer always lands in the DB. A new
``GET /chat/sessions/{id}/stream`` endpoint lets the frontend re-attach to
an in-flight session after a refresh.

Wire format (one event per blank-line-delimited block):

    event: sources
    data: {"hits": [...], "session_id": 42}

    event: delta
    data: {"text": "..."}

    event: done
    data: {"answer": "<full text>", "cited_ids": ["..."], "session_id": 42}

    event: error
    data: {"message": "..."}
"""
from __future__ import annotations

import asyncio
import json
import threading
from typing import AsyncIterator

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from core import chat_history
from core.answerer import extract_cited_ids, stream_answer
from core.embeddings import get_embedding_provider
from core.retrieval import Playbook, detect_language

from ..deps import get_playbook_index
from ..schemas import (
    ChatRequest,
    ChatSessionDetail,
    ChatSessionSummary,
    RetrievalHitOut,
)
from .agent import _hit_to_out


router = APIRouter(prefix="/chat", tags=["chat"])


# Update the row's answer column at most this often (in characters of
# growth) — a refresh mid-stream loses ≤ this many chars from the saved
# row. Smaller = more disk writes; larger = chunkier refresh restore.
_CHECKPOINT_EVERY = 200

# How often the SSE tail polls the DB for new content (seconds).
_TAIL_POLL_INTERVAL = 0.15


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


# ---------------------------------------------------------------------------
# Background generator (lives in a daemon thread; survives client disconnects)
# ---------------------------------------------------------------------------
def _run_generation_thread(
    session_id: int,
    question: str,
    playbooks: list[Playbook],
) -> None:
    """Stream chunks from Claude into the session row. Always runs to
    completion — even if no SSE client is listening — so the final answer
    always lands in the DB."""
    try:
        full_text = ""
        last_checkpoint = 0
        for chunk in stream_answer(question=question, playbooks=playbooks):
            full_text += chunk
            if (len(full_text) - last_checkpoint) >= _CHECKPOINT_EVERY:
                try:
                    chat_history.update_session(session_id, answer=full_text)
                except Exception:
                    pass
                last_checkpoint = len(full_text)
        cited = extract_cited_ids(full_text, playbooks)
        chat_history.update_session(
            session_id,
            answer=full_text,
            cited_ids=cited,
            status="done",
        )
    except Exception as exc:  # noqa: BLE001 — translate to a row-level error
        try:
            chat_history.update_session(
                session_id,
                status="error",
                error_message=str(exc),
            )
        except Exception:
            pass


# Track running threads so we never spawn a duplicate for the same session
# (e.g. if the same session_id is attached twice via the GET stream).
_running_threads: dict[int, threading.Thread] = {}
_threads_lock = threading.Lock()


def _ensure_thread_for(
    session_id: int,
    question: str,
    playbooks: list[Playbook],
) -> None:
    with _threads_lock:
        existing = _running_threads.get(session_id)
        if existing is not None and existing.is_alive():
            return
        thread = threading.Thread(
            target=_run_generation_thread,
            args=(session_id, question, playbooks),
            name=f"chat-gen-{session_id}",
            daemon=True,
        )
        _running_threads[session_id] = thread
        thread.start()


# ---------------------------------------------------------------------------
# SSE tail (reads from DB, yields events)
# ---------------------------------------------------------------------------
async def _sse_tail(session_id: int) -> AsyncIterator[str]:
    """Yield SSE events by tailing the row. Ends when status is done/error.

    Every sync SQLite read is wrapped in ``asyncio.to_thread`` so the
    event loop is never blocked while waiting on disk I/O — without that
    wrapper, a dozen open SSE tails would chain serial sync calls through
    the same coroutine and stall every other request the asyncio loop
    was supposed to dispatch (uvicorn becomes 'SN' / 0% CPU and only
    OPTIONS preflights answer).
    """
    session = await asyncio.to_thread(chat_history.get_session, session_id)
    if session is None:
        yield _sse("error", {"message": f"session {session_id} not found"})
        return

    yield _sse(
        "sources",
        {"hits": session.hits, "session_id": session.id},
    )

    last_pos = len(session.answer)
    if last_pos > 0:
        yield _sse("delta", {"text": session.answer})

    if session.status == "done":
        yield _sse(
            "done",
            {
                "answer": session.answer,
                "cited_ids": session.cited_ids,
                "session_id": session.id,
            },
        )
        return
    if session.status == "error":
        yield _sse(
            "error",
            {"message": session.error_message or "unknown error"},
        )
        return

    while True:
        await asyncio.sleep(_TAIL_POLL_INTERVAL)
        current = await asyncio.to_thread(chat_history.get_session, session_id)
        if current is None:
            yield _sse("error", {"message": f"session {session_id} disappeared"})
            return
        if len(current.answer) > last_pos:
            yield _sse(
                "delta",
                {"text": current.answer[last_pos:]},
            )
            last_pos = len(current.answer)
        if current.status == "done":
            yield _sse(
                "done",
                {
                    "answer": current.answer,
                    "cited_ids": current.cited_ids,
                    "session_id": current.id,
                },
            )
            return
        if current.status == "error":
            yield _sse(
                "error",
                {"message": current.error_message or "unknown error"},
            )
            return


def _sse_response(gen: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(
        gen,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------
@router.post("/answer")
def chat_answer(req: ChatRequest, request: Request) -> StreamingResponse:
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="Empty question")

    index = get_playbook_index(request)

    provider = get_embedding_provider()
    query_vector = np.asarray(provider.embed(req.question), dtype=np.float32)
    hits = index.search(
        query_vector,
        country=None,
        language=detect_language(req.question),
        ticket_class=None,
        top_k=req.top_k,
    )
    hit_payload = [_hit_to_out(h).model_dump() for h in hits]

    # Persist the row up front so any subsequent refresh has something to
    # restore — even if the generator hasn't yielded a single chunk yet.
    session = chat_history.create_pending_session(
        question=req.question,
        hits=hit_payload,
        top_k=req.top_k,
    )

    if not hits:
        # No retrieval result — mark done immediately so the tail terminates.
        chat_history.update_session(session.id, status="done")
    else:
        playbooks = [h.playbook for h in hits]
        _ensure_thread_for(session.id, req.question, playbooks)

    return _sse_response(_sse_tail(session.id))


@router.get("/sessions/{session_id}/stream")
def stream_session(session_id: int, request: Request) -> StreamingResponse:
    """Re-attach to an in-flight (or already finished) chat session.

    Returns the same SSE event sequence as POST /chat/answer would, except
    no new generation thread is started. Used by the frontend on mount when
    rehydrating from localStorage finds a session with status='streaming'.
    """
    session = chat_history.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=404, detail=f"Session {session_id} not found"
        )
    return _sse_response(_sse_tail(session_id))


# ---------------------------------------------------------------------------
# Chat history (list / detail / delete)
# ---------------------------------------------------------------------------
def _session_summary(s: chat_history.ChatSession) -> ChatSessionSummary:
    return ChatSessionSummary(
        id=s.id,
        question=s.question,
        top_k=s.top_k,
        timestamp=s.timestamp,
        source_count=len(s.hits),
        citation_count=len(s.cited_ids),
        status=s.status,
    )


def _session_detail(s: chat_history.ChatSession) -> ChatSessionDetail:
    return ChatSessionDetail(
        **_session_summary(s).model_dump(),
        answer=s.answer,
        hits=[RetrievalHitOut(**h) for h in s.hits],
        cited_ids=s.cited_ids,
        error_message=s.error_message,
    )


@router.get("/sessions", response_model=list[ChatSessionSummary])
def list_sessions(limit: int = 200) -> list[ChatSessionSummary]:
    return [_session_summary(s) for s in chat_history.list_sessions(limit=limit)]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
def get_session(session_id: int) -> ChatSessionDetail:
    session = chat_history.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=404, detail=f"Chat session {session_id} not found"
        )
    return _session_detail(session)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int) -> None:
    deleted = chat_history.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Chat session {session_id} not found"
        )
