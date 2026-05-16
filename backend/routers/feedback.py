"""Approve / edit / reject feedback log endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from core import feedback as feedback_store

from ..schemas import FeedbackRecordOut, FeedbackRequest, FeedbackStats


router = APIRouter(prefix="/feedback", tags=["feedback"])


_VALID_STATUSES = {"approved", "edited", "rejected"}


@router.post("", response_model=FeedbackRecordOut)
def submit_feedback(req: FeedbackRequest) -> FeedbackRecordOut:
    if req.status not in _VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status: {req.status!r}")
    new_id = feedback_store.record_feedback(
        ticket_id=req.ticket_id,
        playbook_id=req.playbook_id,
        draft_text=req.draft_text,
        final_text=req.final_text,
        status=req.status,  # type: ignore[arg-type]
    )
    records = feedback_store.list_feedback(ticket_id=req.ticket_id, limit=1)
    if not records or records[0].id != new_id:
        raise HTTPException(status_code=500, detail="Failed to read back feedback record")
    r = records[0]
    return FeedbackRecordOut(
        id=r.id,
        ticket_id=r.ticket_id,
        playbook_id=r.playbook_id,
        draft_text=r.draft_text,
        final_text=r.final_text,
        status=r.status,
        timestamp=r.timestamp,
    )


@router.get("", response_model=list[FeedbackRecordOut])
def list_feedback(
    ticket_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
) -> list[FeedbackRecordOut]:
    return [
        FeedbackRecordOut(
            id=r.id,
            ticket_id=r.ticket_id,
            playbook_id=r.playbook_id,
            draft_text=r.draft_text,
            final_text=r.final_text,
            status=r.status,
            timestamp=r.timestamp,
        )
        for r in feedback_store.list_feedback(ticket_id=ticket_id, limit=limit)
    ]


@router.get("/stats", response_model=FeedbackStats)
def stats() -> FeedbackStats:
    counts = feedback_store.status_counts()
    return FeedbackStats(
        approved=counts.get("approved", 0),
        edited=counts.get("edited", 0),
        rejected=counts.get("rejected", 0),
        total=sum(counts.values()),
    )
