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
from typing import Any

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
    so a single bad ticket can't stop the batch."""
    ticket_id = str(ticket.get("key") or "")
    if not ticket_id:
        return

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

    # ---- 3. Draft against the top hit ----
    top_pb_id = hits[0].playbook.id
    playbook = next((pb for pb in playbooks if pb.id == top_pb_id), None)
    if playbook is None:
        return
    try:
        draft = draft_reply(
            ticket_summary=summary,
            ticket_description=description,
            playbook=playbook,
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
    # Now that we know which playbook matched, refine the processed mode
    # with any per-playbook override (effective_mode falls back to global
    # if there's no override).
    agent_sessions.mark_processed_mode(
        ticket_id, agent_config.effective_mode(top_pb_id)
    )


def _record_error(ticket_id: str, step: str, exc: Exception) -> None:
    with _batch_lock:
        _batch_state.errors.append(
            {"ticket_id": ticket_id, "step": step, "message": str(exc)}
        )


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
