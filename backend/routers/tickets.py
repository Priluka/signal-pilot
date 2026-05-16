"""Sample-ticket list + detail endpoints."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_tickets
from ..schemas import TicketDetail, TicketSummary


router = APIRouter(prefix="/tickets", tags=["tickets"])


def _summary_from_dict(t: dict[str, Any]) -> TicketSummary:
    return TicketSummary(
        key=str(t.get("key", "?")),
        summary=str(t.get("summary") or ""),
        status=str(t.get("status") or ""),
        status_category=t.get("status_category"),
        priority=t.get("priority"),
        labels=list(t.get("labels") or []),
        reporter_email=t.get("reporter_email"),
        reporter_name=t.get("reporter_name"),
        created_at=t.get("created_at"),
        resolved_at=t.get("resolved_at"),
    )


def _detail_from_dict(t: dict[str, Any]) -> TicketDetail:
    summary = _summary_from_dict(t)
    return TicketDetail(
        **summary.model_dump(),
        description=str(t.get("description") or ""),
        assignee_name=t.get("assignee_name"),
        project_key=t.get("project_key"),
        issue_type=t.get("issue_type"),
        resolution=t.get("resolution"),
        resolution_minutes=t.get("resolution_minutes"),
        comment_count_total=int(t.get("comment_count_total") or 0),
    )


@router.get("", response_model=list[TicketSummary])
def list_tickets(
    tickets: list[dict[str, Any]] = Depends(get_tickets),
) -> list[TicketSummary]:
    return [_summary_from_dict(t) for t in tickets]


@router.get("/{ticket_key}", response_model=TicketDetail)
def get_ticket(
    ticket_key: str,
    tickets: list[dict[str, Any]] = Depends(get_tickets),
) -> TicketDetail:
    for t in tickets:
        if str(t.get("key")) == ticket_key:
            return _detail_from_dict(t)
    raise HTTPException(status_code=404, detail=f"Ticket {ticket_key!r} not found")
