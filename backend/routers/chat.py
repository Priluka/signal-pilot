"""Chat answer endpoint — Server-Sent Events stream.

Wire format (one event per blank-line-delimited block):

    event: sources
    data: {"hits": [...]}

    event: delta
    data: {"text": "..."}

    event: done
    data: {"answer": "<full text>", "cited_ids": ["..."]}

    event: error
    data: {"message": "..."}

The frontend consumes via ``fetch`` + a ReadableStream reader rather than
``EventSource`` (which is GET-only).
"""
from __future__ import annotations

import json
from typing import Iterator

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from core import chat_history
from core.answerer import extract_cited_ids, stream_answer
from core.embeddings import get_embedding_provider
from core.retrieval import detect_language

from ..deps import get_playbook_index
from ..schemas import (
    ChatRequest,
    ChatSessionDetail,
    ChatSessionSummary,
    RetrievalHitOut,
)
from .agent import _hit_to_out


router = APIRouter(prefix="/chat", tags=["chat"])


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.post("/answer")
def chat_answer(req: ChatRequest, request: Request) -> StreamingResponse:
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="Empty question")

    index = get_playbook_index(request)

    # Number of characters added between checkpoint writes during streaming.
    # A page refresh mid-stream loses at most this much text from the DB.
    _CHECKPOINT_EVERY = 250

    def event_stream() -> Iterator[str]:
        try:
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

            # Create the row BEFORE streaming so a refresh mid-stream has
            # something to restore (question + retrieved hits, even if the
            # answer is still partial). session_id rides on the sources
            # event so the frontend can pin it to localStorage immediately.
            session_id: int | None = None
            try:
                session = chat_history.create_pending_session(
                    question=req.question,
                    hits=hit_payload,
                    top_k=req.top_k,
                )
                session_id = session.id
            except Exception:
                pass

            yield _sse(
                "sources",
                {"hits": hit_payload, "session_id": session_id},
            )

            if not hits:
                yield _sse(
                    "done",
                    {"answer": "", "cited_ids": [], "session_id": session_id},
                )
                return

            playbooks = [h.playbook for h in hits]
            full_text = ""
            last_checkpoint = 0
            for chunk in stream_answer(question=req.question, playbooks=playbooks):
                full_text += chunk
                yield _sse("delta", {"text": chunk})
                # Periodic checkpoints so partial answers survive a refresh.
                if (
                    session_id is not None
                    and (len(full_text) - last_checkpoint) >= _CHECKPOINT_EVERY
                ):
                    try:
                        chat_history.update_session(session_id, answer=full_text)
                        last_checkpoint = len(full_text)
                    except Exception:
                        pass

            cited = extract_cited_ids(full_text, playbooks)

            # Final write — answer is complete, citations now known.
            if session_id is not None:
                try:
                    chat_history.update_session(
                        session_id, answer=full_text, cited_ids=cited
                    )
                except Exception:
                    pass

            yield _sse(
                "done",
                {"answer": full_text, "cited_ids": cited, "session_id": session_id},
            )
        except Exception as exc:  # noqa: BLE001 — translate to a single error event
            yield _sse("error", {"message": str(exc)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
def _session_summary(s: chat_history.ChatSession) -> ChatSessionSummary:
    return ChatSessionSummary(
        id=s.id,
        question=s.question,
        top_k=s.top_k,
        timestamp=s.timestamp,
        source_count=len(s.hits),
        citation_count=len(s.cited_ids),
    )


def _session_detail(s: chat_history.ChatSession) -> ChatSessionDetail:
    return ChatSessionDetail(
        **_session_summary(s).model_dump(),
        answer=s.answer,
        hits=[RetrievalHitOut(**h) for h in s.hits],
        cited_ids=s.cited_ids,
    )


@router.get("/sessions", response_model=list[ChatSessionSummary])
def list_sessions(limit: int = 200) -> list[ChatSessionSummary]:
    return [_session_summary(s) for s in chat_history.list_sessions(limit=limit)]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
def get_session(session_id: int) -> ChatSessionDetail:
    session = chat_history.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
    return _session_detail(session)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int) -> None:
    deleted = chat_history.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
