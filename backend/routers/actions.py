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

from core import pending_actions, planner
from core.retrieval import Playbook

from ..deps import get_playbooks


router = APIRouter(prefix="/actions", tags=["actions"])


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


@router.get("/pending", response_model=list[PendingActionOut])
def list_pending() -> list[PendingActionOut]:
    return [_to_out(pa) for pa in pending_actions.list_all()]


@router.get("/pending/{ticket_id}", response_model=list[PendingActionOut])
def list_pending_for_ticket(ticket_id: str) -> list[PendingActionOut]:
    return [_to_out(pa) for pa in pending_actions.list_for_ticket(ticket_id)]


@router.post("/{action_id}/approve", response_model=PlannerResultOut)
def approve(
    action_id: str,
    req: ApproveRequest | None = None,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> PlannerResultOut:
    pa = pending_actions.get(action_id)
    if pa is None:
        raise HTTPException(status_code=404, detail=f"action {action_id} not found")
    result = planner.resume(
        action_id=action_id,
        approved=True,
        edited_input=(req.edited_input if req else None),
        playbooks=playbooks,
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
) -> PlannerResultOut:
    pa = pending_actions.get(action_id)
    if pa is None:
        raise HTTPException(status_code=404, detail=f"action {action_id} not found")
    result = planner.resume(
        action_id=action_id,
        approved=False,
        rejection_note=(req.note if req else None),
        playbooks=playbooks,
    )
    return PlannerResultOut(
        status=result.status,
        pending_action_id=result.pending_action_id,
        error=result.error,
        iterations=result.iterations,
        summary=result.summary,
    )
