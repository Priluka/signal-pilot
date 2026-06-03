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
import logging
import threading
import time
import uuid
from typing import Any, AsyncIterator

import numpy as np
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

import config

log = logging.getLogger(__name__)

from core import chat_history, chat_threads
from core.answerer import extract_all_cited_ids, extract_cited_ids, stream_answer
import re

from core.chat_agent import (
    run_agentic_chat,
    run_agentic_turn,
    self_correct_citations,
    request_interrupt as request_turn_interrupt,
)
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
    AddTurnRequest,
    ChatRequest,
    ChatSessionDetail,
    ChatSessionSummary,
    ChatThreadDetailOut,
    ChatThreadOut,
    ChatThreadSummaryOut,
    ChatTurnOut,
    CitationEntry,
    CreateThreadRequest,
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
# Per-IP rate limiter — Phase 10.
# ---------------------------------------------------------------------------
#
# A misbehaving operator (or an unintended refresh loop) can fire
# enough turns in seconds to either exhaust the Anthropic budget or
# starve the backend. We track per-client-IP request counts in a
# sliding window held in memory. The window is small enough that
# operators never hit it in normal use; a determined offender bounces
# off a 429.

_RATE_LOCK = threading.Lock()
_RATE_BUCKETS: dict[str, list[float]] = {}


def _client_ip(request: "Request") -> str:
    """Best-effort client identity. Honours X-Forwarded-For when behind
    a trusted proxy (treats the leftmost IP as the originator); falls
    back to the raw socket peer. We don't authenticate the header —
    deployment is expected to set it via a reverse proxy that strips
    untrusted forwarded values."""
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"


def _enforce_rate_limit(request: "Request", key_suffix: str = "") -> None:
    """Sliding-window per-IP rate limit. Raises 429 when the bucket is
    full. Called at the top of any endpoint that costs Anthropic
    tokens. ``key_suffix`` lets callers segment buckets per endpoint
    family if needed; for now we share a single bucket across thread
    creation and turn submission since they cost roughly the same."""
    limit = config.CHAT_RATE_LIMIT_TURNS
    window = config.CHAT_RATE_WINDOW_SECONDS
    if limit <= 0:
        return  # disabled
    now = time.time()
    cutoff = now - window
    key = f"{_client_ip(request)}::{key_suffix}"
    with _RATE_LOCK:
        bucket = _RATE_BUCKETS.get(key, [])
        bucket = [t for t in bucket if t > cutoff]
        if len(bucket) >= limit:
            retry_after = max(1, int(window - (now - bucket[0])))
            from core.metrics import CHAT_RATE_LIMIT_HITS

            CHAT_RATE_LIMIT_HITS.inc()
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit: {limit} requests per "
                    f"{window}s exceeded. Retry in {retry_after}s."
                ),
                headers={"Retry-After": str(retry_after)},
            )
        bucket.append(now)
        _RATE_BUCKETS[key] = bucket


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


# ===========================================================================
# Multi-turn chat — threads + turns. Replaces the single-shot ``/chat/agentic``
# path for new conversations; the legacy endpoint stays in place for the
# frontend's existing flow until Phase 4 migrates it.
# ===========================================================================


# Daemon-thread registry keyed by turn_id (each turn is its own
# tool_use loop). Separate from the legacy ``_running_threads`` map so
# session-id collisions can't happen.
_running_turn_threads: dict[int, threading.Thread] = {}
_turn_threads_lock = threading.Lock()


def _turn_to_out(t: chat_threads.ChatTurn) -> ChatTurnOut:
    """Convert the storage dataclass to the API Pydantic model. Sources
    are stored as raw dicts in the row; we wrap them in RetrievalHitOut
    so the response shape matches the rest of the chat API."""
    return ChatTurnOut(
        id=t.id,
        thread_id=t.thread_id,
        turn_index=t.turn_index,
        user_text=t.user_text,
        final_assistant_text=t.final_assistant_text,
        trace=t.trace,
        events=t.events,
        sources=[RetrievalHitOut(**h) for h in t.sources],
        citation_index=[CitationEntry(**c) for c in t.citation_index],
        usage=t.usage,
        status=t.status,
        error_message=t.error_message,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


def _thread_to_out(t: chat_threads.ChatThread) -> ChatThreadOut:
    return ChatThreadOut(
        id=t.id,
        title=t.title,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


def _thread_summary_to_out(
    s: chat_threads.ChatThreadSummary,
) -> ChatThreadSummaryOut:
    return ChatThreadSummaryOut(
        id=s.id,
        title=s.title,
        created_at=s.created_at,
        updated_at=s.updated_at,
        turn_count=s.turn_count,
        last_status=s.last_status,
        last_user_text=s.last_user_text,
    )


# ---------------------------------------------------------------------------
# Daemon thread — wraps run_agentic_turn so the operator's HTTP request
# can return as soon as the SSE tail attaches.
# ---------------------------------------------------------------------------


def _run_turn_thread(
    turn_id: int,
    thread_id: int,
    user_text: str,
    initial_playbook: Playbook,
    playbooks: list[Playbook],
    index: PlaybookIndex | None,
    initial_sources: list[dict[str, Any]],
) -> None:
    """Background driver for one turn. ``run_agentic_turn`` does its own
    persistence (events, trace, status) so this wrapper's only job is
    to catch unhandled exceptions and stamp the turn ``error`` so the
    SSE tail can terminate cleanly. Citation index is computed AFTER
    the loop ends (it needs the full final answer)."""

    def _on_event(kind: str, payload: dict[str, Any]) -> None:  # noqa: ARG001
        # run_agentic_turn already persists events_json itself. The
        # daemon doesn't need to do anything extra per emit — the SSE
        # tail polls the row and forwards new entries.
        return

    # Seed the turn's sources_json so the tail can emit a ``sources``
    # event immediately on attach. The agent might later call
    # search_playbooks and discover OTHER playbooks; those go into
    # events as skill_executed entries, not into sources_json.
    try:
        chat_threads.update_turn(turn_id, sources=initial_sources)
    except Exception:  # noqa: BLE001
        pass

    try:
        result = run_agentic_turn(
            thread_id=thread_id,
            user_text=user_text,
            initial_playbook=initial_playbook,
            on_event=_on_event,
            turn_id=turn_id,  # reuse the row the HTTP handler created
        )
        # Re-read the turn the agent just finished — it may have
        # marked status='error' for a cooperative cancellation
        # (interrupt). In that case we MUST NOT override status with
        # 'done' below; the operator pressed Stop and the error
        # message carries the cancellation marker.
        post_run = chat_threads.get_turn(turn_id)
        answer_text = result.answer
        if post_run is not None and post_run.status == "error":
            # Agent already finalised the row (interrupt path or
            # internal error). Compute citations on whatever final
            # text we have but leave status untouched.
            citation_index = _build_citation_index(
                answer_text, playbooks, index
            )
            chat_threads.update_turn(
                turn_id, citation_index=citation_index
            )
        else:
            # Phase 9C — citation self-correction. If the answer
            # references playbook ids that don't exist anywhere in
            # the corpus, run one corrective rewrite to drop the
            # invalid citations before persisting. Only fires when
            # hallucinations are actually present, so the happy path
            # adds zero LLM cost.
            try:
                valid_ids = (
                    {pb.id for pb in index.playbooks}
                    if index is not None
                    else {pb.id for pb in playbooks}
                )
                corrected, invalid = self_correct_citations(
                    answer_text, valid_ids
                )
                if invalid:
                    answer_text = corrected
                    chat_threads.update_turn(
                        turn_id, final_assistant_text=corrected
                    )
            except Exception:  # noqa: BLE001
                # Self-correction is best-effort — never let a
                # correction-side bug fail the whole turn.
                pass
            citation_index = _build_citation_index(
                answer_text, playbooks, index
            )
            chat_threads.update_turn(
                turn_id,
                citation_index=citation_index,
                status="done",
            )
        _ = extract_cited_ids(answer_text, playbooks)
    except Exception as exc:  # noqa: BLE001
        try:
            chat_threads.update_turn(
                turn_id, status="error", error_message=str(exc)
            )
        except Exception:  # noqa: BLE001
            pass


def _ensure_turn_thread(
    turn_id: int,
    thread_id: int,
    user_text: str,
    initial_playbook: Playbook,
    playbooks: list[Playbook],
    index: PlaybookIndex | None,
    initial_sources: list[dict[str, Any]],
) -> None:
    """Spawn the daemon for one turn — idempotent if a thread is
    already running for the same turn_id (e.g. a duplicate POST while
    the first one's SSE tail is still mid-stream)."""
    # Capture the inbound request id so the daemon's log lines carry
    # the same correlation id as the SSE response that triggered them.
    from backend.main import current_request_id, set_request_id

    rid = current_request_id()

    def _bootstrap() -> None:
        set_request_id(rid)
        log.info(
            "turn daemon start: turn_id=%d thread_id=%d", turn_id, thread_id
        )
        try:
            _run_turn_thread(
                turn_id,
                thread_id,
                user_text,
                initial_playbook,
                playbooks,
                index,
                initial_sources,
            )
            log.info("turn daemon done: turn_id=%d", turn_id)
        except Exception:  # noqa: BLE001
            log.exception("turn daemon crashed: turn_id=%d", turn_id)
            raise

    with _turn_threads_lock:
        existing = _running_turn_threads.get(turn_id)
        if existing is not None and existing.is_alive():
            return
        th = threading.Thread(
            target=_bootstrap,
            name=f"chat-turn-{turn_id}",
            daemon=True,
        )
        _running_turn_threads[turn_id] = th
        th.start()


# ---------------------------------------------------------------------------
# SSE tail for a turn — polls chat_turns.events_json + final_assistant_text
# + status. Same shape as the legacy ``_sse_tail`` but reads from
# chat_turns instead of chat_sessions.
# ---------------------------------------------------------------------------


async def _sse_turn_tail(turn_id: int) -> AsyncIterator[str]:
    turn = await asyncio.to_thread(chat_threads.get_turn, turn_id)
    if turn is None:
        yield _sse("error", {"message": f"turn {turn_id} not found"})
        return

    yield _sse(
        "sources",
        {
            "hits": turn.sources,
            "thread_id": turn.thread_id,
            "turn_id": turn.id,
        },
    )

    # Replay any events captured before the client attached.
    last_event_idx = 0
    for ev in turn.events:
        kind = ev.get("type", "")
        payload = {k: v for k, v in ev.items() if k != "type"}
        if kind:
            yield _sse(kind, payload)
        last_event_idx += 1

    last_pos = len(turn.final_assistant_text)
    if last_pos > 0:
        yield _sse("delta", {"text": turn.final_assistant_text})

    if turn.status == "done":
        yield _sse(
            "done",
            {
                "answer": turn.final_assistant_text,
                "citation_index": turn.citation_index,
                "thread_id": turn.thread_id,
                "turn_id": turn.id,
            },
        )
        return
    if turn.status == "error":
        yield _sse(
            "error",
            {"message": turn.error_message or "unknown error"},
        )
        return

    while True:
        await asyncio.sleep(_TAIL_POLL_INTERVAL)
        current = await asyncio.to_thread(chat_threads.get_turn, turn_id)
        if current is None:
            yield _sse("error", {"message": f"turn {turn_id} disappeared"})
            return
        if len(current.events) > last_event_idx:
            for ev in current.events[last_event_idx:]:
                kind = ev.get("type", "")
                payload = {k: v for k, v in ev.items() if k != "type"}
                if kind:
                    yield _sse(kind, payload)
            last_event_idx = len(current.events)
        if len(current.final_assistant_text) > last_pos:
            yield _sse(
                "delta",
                {"text": current.final_assistant_text[last_pos:]},
            )
            last_pos = len(current.final_assistant_text)
        if current.status == "done":
            yield _sse(
                "done",
                {
                    "answer": current.final_assistant_text,
                    "citation_index": current.citation_index,
                    "thread_id": current.thread_id,
                    "turn_id": current.id,
                },
            )
            return
        if current.status == "error":
            yield _sse(
                "error",
                {"message": current.error_message or "unknown error"},
            )
            return


# ---------------------------------------------------------------------------
# Public thread endpoints
# ---------------------------------------------------------------------------


@router.post("/threads", response_model=ChatThreadOut)
def create_thread(
    request: Request, req: CreateThreadRequest | None = None
) -> ChatThreadOut:
    """Create an empty thread. Title is optional; if omitted, the
    backend rewrites it from the first turn's user_text on landing.
    Frontend can call this on 'New chat' button or implicitly via
    ``POST /chat/threads/{auto}/turns`` once we add that convenience
    route (not in v1)."""
    _enforce_rate_limit(request, key_suffix="thread")
    title = (req.title if req is not None else None)
    t = chat_threads.create_thread(title=title)
    return _thread_to_out(t)


@router.get("/threads", response_model=list[ChatThreadSummaryOut])
def list_threads_endpoint(limit: int = 200) -> list[ChatThreadSummaryOut]:
    """Sidebar list. Newest first. Each row carries turn_count +
    last_status + a preview of the most recent user_text so the
    frontend doesn't fetch per-row."""
    return [
        _thread_summary_to_out(s)
        for s in chat_threads.list_threads(limit=limit)
    ]


@router.get("/threads/{thread_id}", response_model=ChatThreadDetailOut)
def get_thread_detail_endpoint(thread_id: int) -> ChatThreadDetailOut:
    """Thread + every turn in order. Used by the frontend when the
    operator clicks a thread in the sidebar — payload contains
    everything needed to render the conversation."""
    detail = chat_threads.get_thread_detail(thread_id)
    if detail is None:
        raise HTTPException(
            status_code=404, detail=f"Thread {thread_id} not found"
        )
    return ChatThreadDetailOut(
        thread=_thread_to_out(detail.thread),
        turns=[_turn_to_out(t) for t in detail.turns],
    )


@router.delete("/threads/{thread_id}", status_code=204)
def delete_thread_endpoint(thread_id: int) -> None:
    """Delete the thread + all turns (FK cascade)."""
    deleted = chat_threads.delete_thread(thread_id)
    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"Thread {thread_id} not found"
        )


@router.post("/threads/{thread_id}/turns")
def add_turn(
    thread_id: int, req: AddTurnRequest, request: Request
) -> StreamingResponse:
    """Append a new turn to the thread and stream the agent's response
    via SSE. Same protocol as the legacy /chat/agentic endpoint plus
    a ``compacted`` event when the 5-tier compaction kicks in.

    Retrieval runs per-turn: each new user_text is embedded fresh and
    the top hit becomes the ``initial_playbook`` passed to the agent.
    The agent can still pivot via ``search_playbooks`` mid-loop if the
    conversation drifts from that initial match.
    """
    _enforce_rate_limit(request, key_suffix="turn")
    if not req.user_text.strip():
        raise HTTPException(status_code=422, detail="Empty user_text")

    if chat_threads.get_thread(thread_id) is None:
        raise HTTPException(
            status_code=404, detail=f"Thread {thread_id} not found"
        )

    # Phase 11.5 — cumulative per-thread cost cap. Sum usage_json
    # across every prior turn on this thread and reject if it's
    # already at the ceiling. Per-turn cap (Phase 10) protects
    # against runaway single turns; this one stops a long thread
    # from quietly accreting cost across dozens of turns.
    thread_cap = config.CHAT_THREAD_COST_CAP_USD
    if thread_cap > 0:
        prior_cost = 0.0
        for prior in chat_threads.list_turns_for_thread(thread_id):
            prior_cost += float((prior.usage or {}).get("cost_usd") or 0.0)
        if prior_cost >= thread_cap:
            raise HTTPException(
                status_code=402,
                detail=(
                    f"Thread cost cap reached: spent ${prior_cost:.4f} "
                    f">= cap ${thread_cap:.4f}. Start a new thread."
                ),
            )

    index = get_playbook_index(request)
    provider = get_embedding_provider()
    query_vector = np.asarray(
        provider.embed(req.user_text), dtype=np.float32
    )
    text_country = country_from_text(req.user_text)
    hits = index.search(
        query_vector,
        country=text_country,
        language=None if text_country else detect_language(req.user_text),
        ticket_class=None,
        country_boost=text_country,
        keyword_boost_ids=keyword_boosted_playbooks(req.user_text),
        top_k=req.top_k,
    )
    hit_payload = [_hit_to_out(h).model_dump() for h in hits]
    playbooks = [h.playbook for h in hits]
    initial_playbook = playbooks[0] if playbooks else None

    if initial_playbook is None:
        # No hits at all — create a turn marked done with a graceful
        # 'I don't have context for that' answer rather than spinning
        # up the agent loop.
        turn = chat_threads.create_pending_turn(
            thread_id=thread_id, user_text=req.user_text
        )
        chat_threads.update_turn(
            turn.id,
            sources=hit_payload,
            final_assistant_text=(
                "I don't have any playbook context for that question. "
                "Try rephrasing or asking about a specific customer / "
                "plate / ticket."
            ),
            status="done",
        )
        return _sse_response(_sse_turn_tail(turn.id))

    # Create the pending turn FIRST (so the SSE tail has something to
    # attach to), THEN spawn the daemon that runs the agent loop and
    # streams events into the row.
    turn = chat_threads.create_pending_turn(
        thread_id=thread_id, user_text=req.user_text
    )
    _ensure_turn_thread(
        turn_id=turn.id,
        thread_id=thread_id,
        user_text=req.user_text,
        initial_playbook=initial_playbook,
        playbooks=playbooks,
        index=index,
        initial_sources=hit_payload,
    )
    return _sse_response(_sse_turn_tail(turn.id))


@router.post("/threads/{thread_id}/turns/{turn_id}/interrupt", status_code=204)
def interrupt_turn(thread_id: int, turn_id: int) -> None:  # noqa: ARG001
    """Cooperatively cancel a turn that's currently streaming. Backend
    sets a flag; the agent loop checks it at the next iteration
    boundary and exits with ``status='error'`` +
    ``error_message='Cancelled by operator'``. Idempotent — calling
    twice is a no-op.

    Within an iteration the Anthropic stream cannot be killed from
    outside, so an interrupt has up to one full LLM round-trip of
    latency. The UI marks the turn cancelled immediately on the
    client side so the operator sees instant feedback; the server
    state catches up within a few seconds.

    Returns 204 even when the turn doesn't exist — the operator
    doesn't care, and 404 here would race with concurrent
    finish-and-delete flows. Returning 404 only on missing thread
    would be inconsistent with that, so we keep it simple."""
    turn = chat_threads.get_turn(turn_id)
    if turn is not None:
        request_turn_interrupt(turn_id)


@router.get("/threads/{thread_id}/turns/{turn_id}/stream")
def stream_turn(
    thread_id: int, turn_id: int, request: Request  # noqa: ARG001
) -> StreamingResponse:
    """Re-attach to a turn that's mid-stream or already finished.
    Mirrors the legacy ``GET /chat/sessions/{id}/stream`` so the
    frontend can rehydrate on refresh — events_json + final answer
    are replayed first, then live events stream if status is still
    'streaming'.

    ``thread_id`` is in the path mainly for URL clarity; the turn_id
    alone is enough to find the row. We don't 404 on mismatch — if
    the turn exists we serve it.
    """
    turn = chat_threads.get_turn(turn_id)
    if turn is None:
        raise HTTPException(
            status_code=404, detail=f"Turn {turn_id} not found"
        )
    return _sse_response(_sse_turn_tail(turn_id))


# ---------------------------------------------------------------------------
# Retention admin — Phase 12.9.
# ---------------------------------------------------------------------------
#
# The default is ``CHAT_THREAD_RETENTION_DAYS=90``. This endpoint is
# what a daily cron job hits to enforce it; we don't run a background
# scheduler in-process to keep operational behaviour explicit.


@router.post("/admin/threads/purge", tags=["admin"])
def purge_old_threads(older_than_days: int | None = None) -> dict[str, int]:
    """Delete chat threads older than the cutoff. Defaults to the
    configured retention window. Returns ``{"deleted": N}``. Idempotent
    — safe to invoke from a daily cron. FK cascade removes all child
    chat_turns rows automatically."""
    days = (
        older_than_days
        if older_than_days is not None
        else config.CHAT_THREAD_RETENTION_DAYS
    )
    if days <= 0:
        raise HTTPException(
            status_code=422,
            detail="older_than_days must be positive",
        )
    deleted = chat_threads.purge_threads_older_than(days)
    log.info(
        "retention sweep: deleted %d threads older than %d days",
        deleted,
        days,
    )
    return {"deleted": deleted, "older_than_days": days}
