"""Batch processor that drives every sample ticket through the agent pipeline.

When the Agent Feed loads, the frontend triggers ``start_batch`` once. A
daemon thread walks the ticket list, runs classify → retrieve → draft for
each, and persists results into ``agent_sessions``. Subsequent calls are
idempotent — already-complete tickets are skipped.

Module-level ``_batch_state`` is published over ``get_batch_status()`` so
the frontend can render a progress bar and decide when to render the inbox.
"""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator

from core import agent_sessions
from core.classifier import classify_ticket
from core.drafter import draft_reply
from core.retrieval import (
    Playbook,
    PlaybookIndex,
    country_from_labels,
    detect_language,
    retrieve,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class BatchState:
    running: bool = False
    processed: int = 0
    total: int = 0
    started_at: str | None = None
    finished_at: str | None = None
    errors: list[dict[str, str]] = field(default_factory=list)
    current_ticket: str | None = None


_batch_state = BatchState()
_batch_lock = threading.Lock()


# Per-ticket lock map — funnels concurrent process_ticket() calls for
# the SAME ticket id through one at a time. The inbox + /jira/process
# can fire two requests on the same ticket near-simultaneously (e.g.
# user clicks Re-process while a poll-refresh kicks in); without the
# lock both runs would call clear_for_ticket and create separate
# pending actions, doubling Anthropic spend and surfacing duplicate
# approval cards. Tickets that aren't fighting just take their own
# lock and pay no cost.
_ticket_locks: dict[str, threading.Lock] = {}
_ticket_locks_guard = threading.Lock()


def _lock_for_ticket(ticket_id: str) -> threading.Lock:
    with _ticket_locks_guard:
        lock = _ticket_locks.get(ticket_id)
        if lock is None:
            lock = threading.Lock()
            _ticket_locks[ticket_id] = lock
        return lock


def get_batch_status() -> dict[str, Any]:
    with _batch_lock:
        return {
            "running": _batch_state.running,
            "processed": _batch_state.processed,
            "total": _batch_state.total,
            "started_at": _batch_state.started_at,
            "finished_at": _batch_state.finished_at,
            "errors": list(_batch_state.errors),
            "current_ticket": _batch_state.current_ticket,
        }


def _session_is_complete(record: agent_sessions.AgentSessionRecord | None) -> bool:
    """A ticket counts as 'already processed' if we'd produce the same result
    on a re-run: either a terminal state from the operator (feedback) or a
    fully-driven agent verdict (auto-close / draft generated / classification
    skipped it)."""
    if record is None:
        return False
    if record.feedback_status:
        return True
    classification = record.classification or {}
    label = classification.get("label")
    if label in ("internal_log", "spam_or_junk"):
        return True
    if record.draft:
        return True
    return False


def _hit_to_payload(hit: Any) -> dict[str, Any]:
    """Mirror backend.routers.agent._hit_to_out without the FastAPI dependency.
    Kept lightweight so this module doesn't import backend.* — clean layering."""
    pb = hit.playbook
    meta = pb.metadata
    project_keys: set[str] = set()
    for tid in meta.get("evidence_tickets") or []:
        if "-" in str(tid):
            prefix = str(tid).split("-", 1)[0]
            if prefix.isupper():
                project_keys.add(prefix)
    return {
        "playbook_id": pb.id,
        "title": pb.title,
        "description": pb.description,
        "score": hit.score,
        "rank": hit.rank,
        "ticket_class": pb.ticket_class,
        "issue_category": pb.issue_category,
        "country_focus": pb.country_focus,
        "languages": pb.languages,
        "status": str(meta.get("status") or "active"),
        "extraction_confidence": (
            float(meta["extraction_confidence"])
            if meta.get("extraction_confidence") is not None
            else None
        ),
        "project_keys": sorted(project_keys),
    }


def process_ticket(
    ticket: dict[str, Any],
    playbooks: list[Playbook],
    index: PlaybookIndex,
) -> None:
    """Drive one ticket through classify → retrieve → draft. Each step writes
    to ``agent_sessions`` with its own timestamp. Catches per-ticket failures
    so a single bad ticket can't stop the batch.

    Serialized per ticket_id — concurrent calls for the same ticket wait
    on a per-ticket lock so they don't race on planner state."""
    ticket_id = str(ticket.get("key") or "")
    if not ticket_id:
        return

    with _lock_for_ticket(ticket_id):
        _process_ticket_locked(ticket_id, ticket, playbooks, index)


def _process_ticket_locked(
    ticket_id: str,
    ticket: dict[str, Any],
    playbooks: list[Playbook],
    index: PlaybookIndex,
) -> None:
    existing = agent_sessions.get_session(ticket_id)
    if _session_is_complete(existing):
        return

    agent_sessions.mark_started(ticket_id)
    # Stamp the global mode now so any early-return path (skipped /
    # classifier failure / no retrieval hit) still shows what mode the
    # ticket was processed under. If a draft is generated against a
    # playbook with an override, we overwrite this with the playbook's
    # effective mode further down.
    from core import agent_config  # local import to keep module-load fast
    agent_sessions.mark_processed_mode(ticket_id, agent_config.get_mode())

    summary = str(ticket.get("summary") or "")
    description = str(ticket.get("description") or "")
    labels = list(ticket.get("labels") or [])

    # ---- 1. Classify ----
    try:
        result = classify_ticket(
            summary=summary,
            description=description,
            reporter_email=ticket.get("reporter_email"),
            labels=labels,
        )
    except Exception as exc:  # noqa: BLE001
        _record_error(ticket_id, "classify", exc)
        return
    classification_payload = {
        "label": result.label,
        "confidence": result.confidence,
        "reason": result.reason,
    }
    agent_sessions.upsert_classification(ticket_id, classification_payload)

    # Non-support tickets short-circuit — no retrieval, no draft.
    if result.label != "support_request":
        return

    # ---- 2. Retrieve ----
    ticket_text = f"{summary}\n\n{description}".strip()
    try:
        hits = retrieve(
            index,
            ticket_text,
            labels=labels,
            ticket_class=None,
            top_k=3,
        )
    except Exception as exc:  # noqa: BLE001
        _record_error(ticket_id, "retrieve", exc)
        return
    retrieval_payload = {
        "hits": [_hit_to_payload(h) for h in hits],
        "detected_language": detect_language(ticket_text),
        "detected_country": country_from_labels(labels),
    }
    agent_sessions.upsert_retrieval(ticket_id, retrieval_payload)
    if not hits:
        return

    # ---- 3. Route: drafter (single LLM reply) or planner (skills loop) ----
    # Drafter and planner are two mutually exclusive writers, not two
    # stages of one pipeline. A playbook with ``allowed_skills`` goes
    # straight to the planner, which uses tool_use to read context and
    # write the final reply itself. Playbooks without skills keep the
    # classic drafter path.
    top_pb_id = hits[0].playbook.id
    playbook = next((pb for pb in playbooks if pb.id == top_pb_id), None)
    if playbook is None:
        return
    allowed_skills = list(playbook.metadata.get("allowed_skills") or [])
    routing = "planner" if allowed_skills else "drafter"
    agent_sessions.mark_top_playbook(ticket_id, top_pb_id)
    agent_sessions.mark_routing(ticket_id, routing)
    agent_sessions.mark_processed_mode(
        ticket_id, agent_config.effective_mode(top_pb_id)
    )

    if routing == "drafter":
        # Surface attachment presence to the drafter so it can refuse to
        # pretend to have seen a screenshot the customer claimed to send
        # but that didn't actually arrive in the ticket payload. Jira
        # tickets carry attachments under the ``attachment`` field
        # (singular, per the REST API); local sample tickets may use
        # ``attachments`` or omit the field entirely (treated as unknown).
        if "attachments" in ticket:
            has_attachments: bool | None = bool(ticket.get("attachments"))
        elif "attachment" in ticket:
            has_attachments = bool(ticket.get("attachment"))
        else:
            has_attachments = None
        try:
            draft = draft_reply(
                ticket_summary=summary,
                ticket_description=description,
                playbook=playbook,
                has_attachments=has_attachments,
            )
        except Exception as exc:  # noqa: BLE001
            _record_error(ticket_id, "draft", exc)
            return
        draft_payload = {
            "draft": draft.draft,
            "recommended_action": draft.recommended_action,
            "rationale": draft.rationale,
        }
        agent_sessions.upsert_draft(ticket_id, top_pb_id, draft_payload)
        return

    # routing == "planner": skills-driven path, no pre-draft.
    try:
        from core import planner

        result = planner.run(ticket=ticket, playbook=playbook)
        agent_sessions.mark_planner_status(
            ticket_id, result.status, result.error
        )
    except Exception as exc:  # noqa: BLE001
        _record_error(ticket_id, "planner", exc)
        agent_sessions.mark_planner_status(
            ticket_id, "failed", str(exc)
        )


def process_ticket_streaming(
    ticket: dict[str, Any],
    playbooks: list[Playbook],
    index: PlaybookIndex,
) -> Iterator[dict[str, Any]]:
    """Generator twin of ``process_ticket`` — yields one event per milestone.

    Side effects are the same as the blocking variant: each step writes
    its payload to ``agent_sessions`` so the audit log, /agent/sessions
    refresh, and post-stream polling all see consistent state. The
    caller (typically the SSE jira router) just wraps each yielded dict
    in an event frame.

    Event shapes:

      {"type": "started",        "ticket_id": ..., "mode": ..., "at": iso}
      {"type": "classified",     "label": ..., "confidence": ..., "reason": ..., "at": iso}
      {"type": "skipped",        "reason": "non_support_request"}            (terminal)
      {"type": "retrieved",      "hits": [...], "detected_language": ...,
                                 "detected_country": ..., "at": iso}
      {"type": "no_hits"}                                                    (terminal)
      {"type": "drafted",        "playbook_id": ..., "playbook_title": ...,
                                 "recommended_action": ..., "draft": ...,
                                 "rationale": ..., "at": iso}
      {"type": "planner_started","mode": ..., "allowed_skills": [...]}
      {"type": "planner_done",   "status": ..., "summary": ..., "error": ...}
      {"type": "error",          "step": ..., "message": ...}                (terminal)
      {"type": "done",           "ticket_id": ...}                           (always last)
    """
    ticket_id = str(ticket.get("key") or "")
    if not ticket_id:
        yield {"type": "error", "step": "validate", "message": "empty ticket key"}
        return

    with _lock_for_ticket(ticket_id):
        yield from _stream_process_locked(ticket_id, ticket, playbooks, index)


def _stream_process_locked(
    ticket_id: str,
    ticket: dict[str, Any],
    playbooks: list[Playbook],
    index: PlaybookIndex,
) -> Iterator[dict[str, Any]]:
    existing = agent_sessions.get_session(ticket_id)
    if _session_is_complete(existing):
        yield {"type": "done", "ticket_id": ticket_id, "skipped_reason": "already_complete"}
        return

    agent_sessions.mark_started(ticket_id)
    from core import agent_config

    agent_sessions.mark_processed_mode(ticket_id, agent_config.get_mode())
    yield {
        "type": "started",
        "ticket_id": ticket_id,
        "mode": agent_config.get_mode(),
        "at": _now_iso(),
    }

    summary = str(ticket.get("summary") or "")
    description = str(ticket.get("description") or "")
    labels = list(ticket.get("labels") or [])

    # ---- 1. Classify ----
    try:
        result = classify_ticket(
            summary=summary,
            description=description,
            reporter_email=ticket.get("reporter_email"),
            labels=labels,
        )
    except Exception as exc:  # noqa: BLE001
        _record_error(ticket_id, "classify", exc)
        yield {"type": "error", "step": "classify", "message": str(exc)}
        yield {"type": "done", "ticket_id": ticket_id}
        return
    classification_payload = {
        "label": result.label,
        "confidence": result.confidence,
        "reason": result.reason,
    }
    agent_sessions.upsert_classification(ticket_id, classification_payload)
    yield {
        "type": "classified",
        "label": result.label,
        "confidence": result.confidence,
        "reason": result.reason,
        "at": _now_iso(),
    }

    if result.label != "support_request":
        yield {"type": "skipped", "reason": "non_support_request"}
        yield {"type": "done", "ticket_id": ticket_id}
        return

    # ---- 2. Retrieve ----
    ticket_text = f"{summary}\n\n{description}".strip()
    try:
        hits = retrieve(
            index,
            ticket_text,
            labels=labels,
            ticket_class=None,
            top_k=3,
        )
    except Exception as exc:  # noqa: BLE001
        _record_error(ticket_id, "retrieve", exc)
        yield {"type": "error", "step": "retrieve", "message": str(exc)}
        yield {"type": "done", "ticket_id": ticket_id}
        return
    retrieval_payload = {
        "hits": [_hit_to_payload(h) for h in hits],
        "detected_language": detect_language(ticket_text),
        "detected_country": country_from_labels(labels),
    }
    agent_sessions.upsert_retrieval(ticket_id, retrieval_payload)
    if not hits:
        # Emit retrieved with no routing — there's nothing downstream.
        yield {
            "type": "retrieved",
            "hits": retrieval_payload["hits"],
            "detected_language": retrieval_payload["detected_language"],
            "detected_country": retrieval_payload["detected_country"],
            "routing": None,
            "at": _now_iso(),
        }
        yield {"type": "no_hits"}
        yield {"type": "done", "ticket_id": ticket_id}
        return

    # ---- 3. Route: drafter or planner (mutually exclusive) ----
    top_pb_id = hits[0].playbook.id
    playbook = next((pb for pb in playbooks if pb.id == top_pb_id), None)
    if playbook is None:
        yield {
            "type": "retrieved",
            "hits": retrieval_payload["hits"],
            "detected_language": retrieval_payload["detected_language"],
            "detected_country": retrieval_payload["detected_country"],
            "routing": None,
            "at": _now_iso(),
        }
        yield {"type": "error", "step": "draft", "message": f"playbook {top_pb_id} not loaded"}
        yield {"type": "done", "ticket_id": ticket_id}
        return
    allowed_skills = list(playbook.metadata.get("allowed_skills") or [])
    routing = "planner" if allowed_skills else "drafter"
    agent_sessions.mark_top_playbook(ticket_id, top_pb_id)
    agent_sessions.mark_routing(ticket_id, routing)
    agent_sessions.mark_processed_mode(
        ticket_id, agent_config.effective_mode(top_pb_id)
    )
    # Surface routing in the retrieved event so the timeline knows
    # immediately whether the next active stage is "drafting" or "planning"
    # — without it the placeholder would have to guess during the gap
    # before the next event arrives.
    yield {
        "type": "retrieved",
        "hits": retrieval_payload["hits"],
        "detected_language": retrieval_payload["detected_language"],
        "detected_country": retrieval_payload["detected_country"],
        "routing": routing,
        "at": _now_iso(),
    }

    if routing == "drafter":
        if "attachments" in ticket:
            has_attachments: bool | None = bool(ticket.get("attachments"))
        elif "attachment" in ticket:
            has_attachments = bool(ticket.get("attachment"))
        else:
            has_attachments = None
        try:
            draft = draft_reply(
                ticket_summary=summary,
                ticket_description=description,
                playbook=playbook,
                has_attachments=has_attachments,
            )
        except Exception as exc:  # noqa: BLE001
            _record_error(ticket_id, "draft", exc)
            yield {"type": "error", "step": "draft", "message": str(exc)}
            yield {"type": "done", "ticket_id": ticket_id}
            return
        draft_payload = {
            "draft": draft.draft,
            "recommended_action": draft.recommended_action,
            "rationale": draft.rationale,
        }
        agent_sessions.upsert_draft(ticket_id, top_pb_id, draft_payload)
        yield {
            "type": "drafted",
            "playbook_id": top_pb_id,
            "playbook_title": playbook.title,
            "recommended_action": draft.recommended_action,
            "draft": draft.draft,
            "rationale": draft.rationale,
            "at": _now_iso(),
        }
        yield {"type": "done", "ticket_id": ticket_id}
        return

    # routing == "planner"
    yield {
        "type": "planner_started",
        "mode": agent_config.effective_mode(top_pb_id),
        "allowed_skills": allowed_skills,
        "playbook_id": top_pb_id,
        "playbook_title": playbook.title,
    }
    try:
        from core import planner

        pres = planner.run(ticket=ticket, playbook=playbook)
        agent_sessions.mark_planner_status(ticket_id, pres.status, pres.error)
        yield {
            "type": "planner_done",
            "status": pres.status,
            "summary": pres.summary,
            "error": pres.error,
            "iterations": pres.iterations,
            "pending_action_id": pres.pending_action_id,
        }
    except Exception as exc:  # noqa: BLE001
        _record_error(ticket_id, "planner", exc)
        agent_sessions.mark_planner_status(ticket_id, "failed", str(exc))
        yield {"type": "error", "step": "planner", "message": str(exc)}

    yield {"type": "done", "ticket_id": ticket_id}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _record_error(ticket_id: str, step: str, exc: Exception) -> None:
    msg = str(exc)
    with _batch_lock:
        _batch_state.errors.append(
            {"ticket_id": ticket_id, "step": step, "message": msg}
        )
    # Persist to agent_sessions so a page refresh after the failure
    # shows the same red error step the live SSE stream did, instead
    # of an infinite spinner that frontends derive from missing
    # classified_at / planner_status. The DB write is best-effort —
    # if it fails (e.g. disk error during shutdown) we still preserve
    # the in-memory batch record above.
    try:
        agent_sessions.mark_error(ticket_id, step, msg)
    except Exception:  # noqa: BLE001
        pass


def start_batch(
    tickets: list[dict[str, Any]],
    playbooks: list[Playbook],
    index: PlaybookIndex,
) -> dict[str, Any]:
    """Spawn (or no-op if already running) the background batch processor."""
    with _batch_lock:
        if _batch_state.running:
            return get_batch_status()
        _batch_state.running = True
        _batch_state.processed = 0
        _batch_state.total = len(tickets)
        _batch_state.started_at = _now()
        _batch_state.finished_at = None
        _batch_state.errors = []
        _batch_state.current_ticket = None

    def run() -> None:
        try:
            for ticket in tickets:
                with _batch_lock:
                    _batch_state.current_ticket = str(ticket.get("key") or "")
                process_ticket(ticket, playbooks, index)
                with _batch_lock:
                    _batch_state.processed += 1
        finally:
            with _batch_lock:
                _batch_state.running = False
                _batch_state.finished_at = _now()
                _batch_state.current_ticket = None

    threading.Thread(target=run, name="agent-batch", daemon=True).start()
    return get_batch_status()
