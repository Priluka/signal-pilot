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

from core.answerer import extract_cited_ids, stream_answer
from core.embeddings import get_embedding_provider
from core.retrieval import detect_language

from ..deps import get_playbook_index
from ..schemas import ChatRequest
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
                yield _sse("done", {"answer": "", "cited_ids": []})
                return

            playbooks = [h.playbook for h in hits]
            full_text = ""
            for chunk in stream_answer(question=req.question, playbooks=playbooks):
                full_text += chunk
                yield _sse("delta", {"text": chunk})

            cited = extract_cited_ids(full_text, playbooks)
            yield _sse("done", {"answer": full_text, "cited_ids": cited})
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
