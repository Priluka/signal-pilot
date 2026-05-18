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
            yield _sse(
                "sources",
                {"hits": [_hit_to_out(h).model_dump() for h in hits]},
            )

            if not hits:
                yield _sse("done", {"answer": "", "cited_ids": [], "session_id": None})
                return

            playbooks = [h.playbook for h in hits]
            full_text = ""
            for chunk in stream_answer(question=req.question, playbooks=playbooks):
                full_text += chunk
                yield _sse("delta", {"text": chunk})

            cited = extract_cited_ids(full_text, playbooks)

            # Persist the completed session so the Chat tab's history rail
            # has something to show. Best-effort: if persistence fails we
            # still hand the answer back to the client.
            session_id: int | None = None
            try:
                session = chat_history.record_session(
                    question=req.question,
                    answer=full_text,
                    hits=[_hit_to_out(h).model_dump() for h in hits],
                    cited_ids=cited,
                    top_k=req.top_k,
                )
                session_id = session.id
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
