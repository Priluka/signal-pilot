"""Operator-submitted playbook edit suggestions."""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from core import suggestions as suggestions_store
from core.retrieval import Playbook, load_playbook

from ..deps import get_playbooks
from ..schemas import SuggestionRecordOut, SuggestionRequest, SuggestionStats


router = APIRouter(prefix="/suggestions", tags=["suggestions"])


def _to_out(r: suggestions_store.SuggestionRecord) -> SuggestionRecordOut:
    return SuggestionRecordOut(
        id=r.id,
        playbook_id=r.playbook_id,
        section=r.section,
        step_number=r.step_number,
        old_text=r.old_text,
        new_text=r.new_text,
        author=r.author,
        status=r.status,
        timestamp=r.timestamp,
    )


@router.post("", response_model=SuggestionRecordOut)
def submit_suggestion(req: SuggestionRequest) -> SuggestionRecordOut:
    if not req.playbook_id.strip() or not req.old_text or not req.new_text.strip():
        raise HTTPException(
            status_code=422,
            detail="playbook_id, old_text, and new_text are required",
        )
    record = suggestions_store.record_suggestion(
        playbook_id=req.playbook_id,
        section=req.section,
        step_number=req.step_number,
        old_text=req.old_text,
        new_text=req.new_text,
        author=req.author or "anonymous",
    )
    return _to_out(record)


@router.get("", response_model=list[SuggestionRecordOut])
def list_suggestions(
    playbook_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
) -> list[SuggestionRecordOut]:
    return [
        _to_out(r)
        for r in suggestions_store.list_suggestions(
            playbook_id=playbook_id,
            status=status,  # type: ignore[arg-type]
            limit=limit,
        )
    ]


@router.get("/stats", response_model=SuggestionStats)
def stats() -> SuggestionStats:
    rows = suggestions_store.list_suggestions(limit=1000)
    counts = {"pending": 0, "accepted": 0, "rejected": 0}
    for r in rows:
        if r.status in counts:
            counts[r.status] += 1
    return SuggestionStats(
        pending=counts["pending"],
        accepted=counts["accepted"],
        rejected=counts["rejected"],
        total=sum(counts.values()),
    )


@router.put("/{suggestion_id}/accept", response_model=SuggestionRecordOut)
def accept(
    suggestion_id: int,
    request: Request,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> SuggestionRecordOut:
    by_id = {pb.id: pb for pb in playbooks}

    def lookup(pb_id: str) -> Path | None:
        pb = by_id.get(pb_id)
        return pb.path if pb else None

    try:
        record = suggestions_store.accept_suggestion(
            suggestion_id, playbook_path_lookup=lookup
        )
    except suggestions_store.SuggestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)

    # Refresh the in-memory playbook so the API serves the new content
    # immediately. Invalidate the embedding index too — body changed.
    for i, pb in enumerate(playbooks):
        if pb.id == record.playbook_id:
            playbooks[i] = load_playbook(pb.path)
            break
    request.app.state.index = None

    return _to_out(record)


@router.put("/{suggestion_id}/reject", response_model=SuggestionRecordOut)
def reject(suggestion_id: int) -> SuggestionRecordOut:
    try:
        record = suggestions_store.reject_suggestion(suggestion_id)
    except suggestions_store.SuggestionError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    return _to_out(record)
