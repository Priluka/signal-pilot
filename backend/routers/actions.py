"""HITL approval endpoints — frontend glue for the planner's pause/resume.

Three endpoints:

- ``GET /actions/pending``                        — full list (for global badges)
- ``GET /actions/pending/{ticket_id}``            — ticket-scoped list (detail view)
- ``POST /actions/{action_id}/approve``           — operator approves; planner resumes
- ``POST /actions/{action_id}/reject``            — operator rejects with reason

Approve/reject return the planner's new outcome — ``done``, another
``awaiting_approval`` (if the loop produced a second write tool), or
``failed`` / ``max_iterations``.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core import agent_audit, agent_sessions, pending_actions, planner
from core.retrieval import Playbook

from ..auth import require_operator
from ..deps import get_playbooks


# Auth applied at the router level so every endpoint inherits it. When
# OPERATOR_TOKEN is unset (dev), require_operator is a no-op returning
# "anonymous-dev"; otherwise it 401s anything without a valid bearer.
router = APIRouter(
    prefix="/actions",
    tags=["actions"],
    dependencies=[Depends(require_operator)],
)


# ---------------------------------------------------------------------------
# Response / request shapes
# ---------------------------------------------------------------------------


class PendingActionOut(BaseModel):
    """One paused tool_use surfaced to the frontend approval panel."""

    id: str
    ticket_id: str
    playbook_id: str
    skill_name: str
    skill_input: dict[str, Any]
    mode: str
    iteration: int
    created_at: str


class PlannerResultOut(BaseModel):
    """Outcome returned by approve / reject — mirrors PlannerResult."""

    status: str
    pending_action_id: str | None = None
    error: str | None = None
    iterations: int = 0
    summary: str | None = None


class ApproveRequest(BaseModel):
    """Optional input override — the operator can edit params before sending."""

    edited_input: dict[str, Any] | None = None


class RejectRequest(BaseModel):
    """Optional reason — fed back to Claude as the tool_result so it can try again."""

    note: str | None = Field(default=None, max_length=500)


class AuditEntryOut(BaseModel):
    """Append-only audit row — never deleted, fed to compliance/BI."""

    id: int
    ticket_id: str
    playbook_id: str
    skill_name: str
    skill_input: dict[str, Any]
    outcome: str
    ok: bool
    result_data: dict[str, Any] | None = None
    error: str | None = None
    decided_by: str | None = None
    mode: str
    iteration: int
    decided_at: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


def _to_out(pa: pending_actions.PendingAction) -> PendingActionOut:
    return PendingActionOut(
        id=pa.id,
        ticket_id=pa.ticket_id,
        playbook_id=pa.playbook_id,
        skill_name=pa.skill_name,
        skill_input=pa.skill_input,
        mode=pa.mode,
        iteration=pa.iteration,
        created_at=pa.created_at,
    )


def _audit_to_out(e: agent_audit.AuditEntry) -> AuditEntryOut:
    return AuditEntryOut(
        id=e.id,
        ticket_id=e.ticket_id,
        playbook_id=e.playbook_id,
        skill_name=e.skill_name,
        skill_input=e.skill_input,
        outcome=e.outcome,
        ok=e.ok,
        result_data=e.result_data,
        error=e.error,
        decided_by=e.decided_by,
        mode=e.mode,
        iteration=e.iteration,
        decided_at=e.decided_at,
    )


@router.get("/pending", response_model=list[PendingActionOut])
def list_pending() -> list[PendingActionOut]:
    return [_to_out(pa) for pa in pending_actions.list_all()]


@router.get("/history", response_model=list[AuditEntryOut])
def list_history(limit: int = 200) -> list[AuditEntryOut]:
    """Append-only audit log — every executed skill in reverse-chrono order."""
    return [_audit_to_out(e) for e in agent_audit.list_recent(limit=limit)]


@router.get("/history/{ticket_id}", response_model=list[AuditEntryOut])
def list_history_for_ticket(ticket_id: str) -> list[AuditEntryOut]:
    return [_audit_to_out(e) for e in agent_audit.list_for_ticket(ticket_id)]


@router.get("/pending/{ticket_id}", response_model=list[PendingActionOut])
def list_pending_for_ticket(ticket_id: str) -> list[PendingActionOut]:
    return [_to_out(pa) for pa in pending_actions.list_for_ticket(ticket_id)]


@router.post("/{action_id}/approve", response_model=PlannerResultOut)
def approve(
    action_id: str,
    req: ApproveRequest | None = None,
    playbooks: list[Playbook] = Depends(get_playbooks),
    operator: str = Depends(require_operator),
) -> PlannerResultOut:
    # Atomic claim — second concurrent request gets 409 instead of
    # re-executing the same skill. The lookup that follows the claim is
    # purely for the ticket_id needed to mark the session status.
    pa = pending_actions.claim(action_id)
    if pa is None:
        # Either gone or already claimed. Both are 409: client shouldn't
        # retry; a UI poll will pick up the new state.
        raise HTTPException(
            status_code=409,
            detail=f"action {action_id} is gone or already in flight",
        )
    result = planner.resume(
        action_id=action_id,
        approved=True,
        edited_input=(req.edited_input if req else None),
        decided_by=operator,
        playbooks=playbooks,
    )
    agent_sessions.mark_planner_status(
        pa.ticket_id, result.status, result.error
    )
    return PlannerResultOut(
        status=result.status,
        pending_action_id=result.pending_action_id,
        error=result.error,
        iterations=result.iterations,
        summary=result.summary,
    )


@router.post("/{action_id}/reject", response_model=PlannerResultOut)
def reject(
    action_id: str,
    req: RejectRequest | None = None,
    playbooks: list[Playbook] = Depends(get_playbooks),
    operator: str = Depends(require_operator),
) -> PlannerResultOut:
    pa = pending_actions.claim(action_id)
    if pa is None:
        raise HTTPException(
            status_code=409,
            detail=f"action {action_id} is gone or already in flight",
        )
    result = planner.resume(
        action_id=action_id,
        approved=False,
        rejection_note=(req.note if req else None),
        decided_by=operator,
        playbooks=playbooks,
    )
    agent_sessions.mark_planner_status(
        pa.ticket_id, result.status, result.error
    )
    return PlannerResultOut(
        status=result.status,
        pending_action_id=result.pending_action_id,
        error=result.error,
        iterations=result.iterations,
        summary=result.summary,
    )
