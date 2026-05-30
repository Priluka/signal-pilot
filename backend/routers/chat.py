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
from typing import Any, AsyncIterator

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from core import chat_history
from core.answerer import extract_all_cited_ids, extract_cited_ids, stream_answer
import re

from core.chat_agent import run_agentic_chat
from core.embeddings import get_embedding_provider
from core.skills.registry import REGISTRY


# Tokens that look like a vehicle plate (Austrian W-55123K, Croatian
# ZG-1234-AB, Slovak SK334AB, German DE-MH-5521, Italian I-AM442RR, …).
# Permissive on purpose: starts with a letter, total length 5-12, may
# contain dashes. A false positive (e.g. "FAQ-2025") triggers a few
# read lookups that come back empty — cheaper than a false negative
# which leaves the agent answering from playbook prose alone when the
# operator clearly asked for concrete data on a specific record.
_PLATE_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9-]{4,11}\b")

# Default read-only skill set the router injects whenever a plate is
# detected, regardless of which playbook matched. Mirrors what every
# skills-enabled playbook lists. Pure how-to questions don't trip
# this path and continue to use whatever the matched playbook offers
# (or fall back to the legacy answerer).
_DEFAULT_PLATE_SKILLS = [
    "bmove_user_lookup",
    "skidata_session_lookup",
    "graylog_search",
    "parkis_lookup",
    "datatrans_transaction",
]


def _looks_like_plate(question: str) -> bool:
    """True iff the question contains a token that resembles a plate."""
    for token in _PLATE_TOKEN_RE.findall(question.upper()):
        if any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
            return True
    return False
from core.retrieval import (
    Playbook,
    PlaybookIndex,
    country_from_text,
    detect_language,
    keyword_boosted_playbooks,
)

from ..deps import get_playbook_index
from ..schemas import (
    ChatRequest,
    ChatSessionDetail,
    ChatSessionSummary,
    CitationEntry,
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


def _build_citation_index(
    answer_text: str,
    playbooks: list[Playbook],
    index: PlaybookIndex | None,
) -> list[dict]:
    """Resolve every ``[id]`` in the answer against the full corpus.

    Every citation that appears in the prose is looked up against the
    full playbook index — not just the top-K we showed the model — so
    the UI can render each one as a proper numbered, clickable link
    instead of an unknown-source ``?``. The ``in_topk`` flag preserves
    the distinction between "the model anchored on what we gave it" and
    "the model knew about this from elsewhere".

    ``exists=False`` rows mean the id wasn't found anywhere in the
    corpus — the model hallucinated it. The frontend drops these from
    the rendered prose so the operator never sees a broken citation.
    """
    topk_ids = {pb.id for pb in playbooks}
    topk_by_id = {pb.id: pb for pb in playbooks}
    out: list[dict] = []
    for cid in extract_all_cited_ids(answer_text):
        in_topk = cid in topk_ids
        if in_topk:
            pb = topk_by_id[cid]
            out.append({
                "playbook_id": cid,
                "title": pb.title,
                "description": (pb.description or "")[:280],
                "in_topk": True,
                "exists": True,
            })
            continue
        pb = index.get(cid) if index is not None else None
        if pb is not None:
            out.append({
                "playbook_id": cid,
                "title": pb.title,
                "description": (pb.description or "")[:280],
                "in_topk": False,
                "exists": True,
            })
        else:
            out.append({
                "playbook_id": cid,
                "title": "",
                "description": "",
                "in_topk": False,
                "exists": False,
            })
    return out


# ---------------------------------------------------------------------------
# Background generator (lives in a daemon thread; survives client disconnects)
# ---------------------------------------------------------------------------
def _run_generation_thread(
    session_id: int,
    question: str,
    playbooks: list[Playbook],
    index: PlaybookIndex | None,
) -> None:
    """Stream chunks from Claude into the session row. Always runs to
    completion — even if no SSE client is listening — so the final answer
    always lands in the DB.

    After the model finishes, we resolve every ``[id]`` in the answer
    against the full playbook corpus (``index``) and persist a
    ``citation_index`` so the UI can render every citation as a real
    numbered link, even ones that point to playbooks outside the
    retrieved top-K.
    """
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
        citation_index = _build_citation_index(full_text, playbooks, index)
        chat_history.update_session(
            session_id,
            answer=full_text,
            cited_ids=cited,
            citation_index=citation_index,
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


# ---------------------------------------------------------------------------
# Agentic generation thread — tool_use loop + token-by-token streaming
# ---------------------------------------------------------------------------


def _run_agentic_thread(
    session_id: int,
    question: str,
    playbook: Playbook,
    playbooks: list[Playbook],
    index: PlaybookIndex | None,
    extra_skills: list[str] | None = None,
) -> None:
    """Drive the chat_agent loop and stream output into the session row.

    Mirrors ``_run_generation_thread`` for legacy chat but additionally
    persists each skill_executing / skill_executed event so a reconnect
    can replay the skill timeline. Daemon-style: keeps running to
    completion regardless of whether any SSE tail is attached.
    """
    events: list[dict[str, Any]] = []
    full_text = ""
    last_checkpoint = 0

    def _on_event(kind: str, payload: dict[str, Any]) -> None:
        nonlocal full_text, last_checkpoint
        if kind == "token":
            full_text += payload.get("text", "")
            if (len(full_text) - last_checkpoint) >= _CHECKPOINT_EVERY:
                try:
                    chat_history.update_session(session_id, answer=full_text)
                except Exception:
                    pass
                last_checkpoint = len(full_text)
            return
        # composing / skill_executing / skill_executed — append to the
        # events list and persist after every entry. These rows are small
        # (a few hundred bytes each, with skill results compactly JSON'd)
        # and there are typically 3-8 per query, so the write cost is
        # negligible.
        events.append({"type": kind, **payload})
        try:
            chat_history.update_session(session_id, events=events)
        except Exception:
            pass

    try:
        result = run_agentic_chat(
            question=question,
            playbook=playbook,
            on_event=_on_event,
            extra_skills=extra_skills,
        )
        # Final write — flush everything in one go so the SSE tail's
        # next poll sees a consistent terminal state.
        cited = extract_cited_ids(result.answer, playbooks)
        citation_index = _build_citation_index(result.answer, playbooks, index)
        chat_history.update_session(
            session_id,
            answer=result.answer,
            cited_ids=cited,
            citation_index=citation_index,
            events=events,
            status="done",
        )
    except Exception as exc:  # noqa: BLE001
        try:
            chat_history.update_session(
                session_id,
                events=events,
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
    index: PlaybookIndex | None,
) -> None:
    with _threads_lock:
        existing = _running_threads.get(session_id)
        if existing is not None and existing.is_alive():
            return
        thread = threading.Thread(
            target=_run_generation_thread,
            args=(session_id, question, playbooks, index),
            name=f"chat-gen-{session_id}",
            daemon=True,
        )
        _running_threads[session_id] = thread
        thread.start()


def _ensure_agentic_thread_for(
    session_id: int,
    question: str,
    playbook: Playbook,
    playbooks: list[Playbook],
    index: PlaybookIndex | None,
    extra_skills: list[str] | None = None,
) -> None:
    """Agentic counterpart of ``_ensure_thread_for`` — single ``playbook``
    drives tool selection, full ``playbooks`` list stays around for
    citation resolution at the end. ``extra_skills`` augments the
    playbook's ``allowed_skills`` (used for plate-forced agentic mode)."""
    with _threads_lock:
        existing = _running_threads.get(session_id)
        if existing is not None and existing.is_alive():
            return
        thread = threading.Thread(
            target=_run_agentic_thread,
            args=(session_id, question, playbook, playbooks, index, extra_skills),
            name=f"chat-agentic-{session_id}",
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

    # Agentic events captured before the client connected. Replay them
    # in order so the operator sees the full skill timeline that
    # produced the answer they're about to read. Legacy text-only chat
    # rows have events=[] so this is a no-op for them.
    last_event_idx = 0
    for ev in session.events:
        kind = ev.get("type", "")
        payload = {k: v for k, v in ev.items() if k != "type"}
        if kind:
            yield _sse(kind, payload)
        last_event_idx += 1

    last_pos = len(session.answer)
    if last_pos > 0:
        yield _sse("delta", {"text": session.answer})

    if session.status == "done":
        yield _sse(
            "done",
            {
                "answer": session.answer,
                "cited_ids": session.cited_ids,
                "citation_index": session.citation_index,
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
        # New agentic events since last poll — emit in order.
        if len(current.events) > last_event_idx:
            for ev in current.events[last_event_idx:]:
                kind = ev.get("type", "")
                payload = {k: v for k, v in ev.items() if k != "type"}
                if kind:
                    yield _sse(kind, payload)
            last_event_idx = len(current.events)
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
                    "citation_index": current.citation_index,
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
    # Free-text country/city detection: if the operator wrote "stuck
    # session u Beču" or "Italian invoice requests" we want the
    # country-specific playbook even though the sentence language is
    # Croatian/English. When a country signal is present we drop the
    # language filter (the query language is the operator's voice, not
    # the location's) and apply the boost so close calls go the right
    # way.
    text_country = country_from_text(req.question)
    hits = index.search(
        query_vector,
        country=text_country,
        language=None if text_country else detect_language(req.question),
        ticket_class=None,
        country_boost=text_country,
        keyword_boost_ids=keyword_boosted_playbooks(req.question),
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
        _ensure_thread_for(session.id, req.question, playbooks, index)

    return _sse_response(_sse_tail(session.id))


@router.post("/agentic")
def chat_agentic(req: ChatRequest, request: Request) -> StreamingResponse:
    """Agentic chat: if the top retrieved playbook has ``allowed_skills``,
    drive the chat_agent loop (real lookups → grounded answer); otherwise
    fall through to plain answerer.stream_answer. SSE schema is the
    superset of ``/chat/answer`` plus ``composing`` / ``skill_executing``
    / ``skill_executed`` events.
    """
    if not req.question.strip():
        raise HTTPException(status_code=422, detail="Empty question")

    index = get_playbook_index(request)
    provider = get_embedding_provider()
    query_vector = np.asarray(provider.embed(req.question), dtype=np.float32)
    text_country = country_from_text(req.question)
    hits = index.search(
        query_vector,
        country=text_country,
        language=None if text_country else detect_language(req.question),
        ticket_class=None,
        country_boost=text_country,
        keyword_boost_ids=keyword_boosted_playbooks(req.question),
        top_k=req.top_k,
    )
    hit_payload = [_hit_to_out(h).model_dump() for h in hits]
    session = chat_history.create_pending_session(
        question=req.question,
        hits=hit_payload,
        top_k=req.top_k,
    )

    if not hits:
        chat_history.update_session(session.id, status="done")
        return _sse_response(_sse_tail(session.id))

    playbooks = [h.playbook for h in hits]
    top_playbook = playbooks[0]
    allowed_skills = top_playbook.metadata.get("allowed_skills") or []
    has_read_skills = any(
        (cls := REGISTRY.get(name)) is not None and not cls.is_write
        for name in allowed_skills
    )
    plate_in_question = _looks_like_plate(req.question)
    # Routing:
    #   • Plate in the question (e.g. "Provjeri W-55123K") → force
    #     agentic with the default lookup set, regardless of which
    #     playbook matched. The operator wants real data, not playbook
    #     prose. Catches the case where retrieval lands on a playbook
    #     without allowed_skills (PKC-misuse cluster, generic how-tos)
    #     even though the question is clearly about a specific record.
    #   • Otherwise: agentic when the matched playbook lists at least
    #     one read skill; legacy text-only chat when it doesn't.
    if plate_in_question or has_read_skills:
        extra = list(_DEFAULT_PLATE_SKILLS) if plate_in_question else None
        _ensure_agentic_thread_for(
            session.id, req.question, top_playbook, playbooks, index, extra
        )
    else:
        _ensure_thread_for(session.id, req.question, playbooks, index)
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


def _session_detail(
    s: chat_history.ChatSession,
    index: PlaybookIndex | None = None,
) -> ChatSessionDetail:
    citation_index = s.citation_index
    # Lazy backfill: rows persisted before the citation_index column existed
    # (or whose generation thread predated this feature) get one computed on
    # read so the operator sees fully-resolved citations even on old sessions.
    if (
        not citation_index
        and s.answer
        and s.status == "done"
        and index is not None
    ):
        topk_playbooks = []
        for h in s.hits:
            pb = index.get(h.get("playbook_id", ""))
            if pb is not None:
                topk_playbooks.append(pb)
        citation_index = _build_citation_index(s.answer, topk_playbooks, index)
        if citation_index:
            try:
                chat_history.update_session(s.id, citation_index=citation_index)
            except Exception:
                pass
    return ChatSessionDetail(
        **_session_summary(s).model_dump(),
        answer=s.answer,
        hits=[RetrievalHitOut(**h) for h in s.hits],
        cited_ids=s.cited_ids,
        citation_index=[CitationEntry(**c) for c in citation_index],
        error_message=s.error_message,
        events=s.events,
    )


@router.get("/sessions", response_model=list[ChatSessionSummary])
def list_sessions(limit: int = 200) -> list[ChatSessionSummary]:
    return [_session_summary(s) for s in chat_history.list_sessions(limit=limit)]


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
def get_session(session_id: int, request: Request) -> ChatSessionDetail:
    session = chat_history.get_session(session_id)
    if session is None:
        raise HTTPException(
            status_code=404, detail=f"Chat session {session_id} not found"
        )
    index = get_playbook_index(request)
    return _session_detail(session, index)


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: int) -> None:
    deleted = chat_history.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Chat session {session_id} not found"
        )
