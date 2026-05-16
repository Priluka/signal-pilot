"""Operator-submitted playbook edit suggestions."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from core import suggestions as suggestions_store

from ..schemas import SuggestionRecordOut, SuggestionRequest


router = APIRouter(prefix="/suggestions", tags=["suggestions"])


def _to_out(r: suggestions_store.SuggestionRecord) -> SuggestionRecordOut:
    return SuggestionRecordOut(
        id=r.id,
        playbook_id=r.playbook_id,
        text=r.text,
        status=r.status,
        timestamp=r.timestamp,
    )


@router.post("", response_model=SuggestionRecordOut)
def submit_suggestion(req: SuggestionRequest) -> SuggestionRecordOut:
    if not req.playbook_id.strip() or not req.text.strip():
        raise HTTPException(status_code=422, detail="playbook_id and text are required")
    record = suggestions_store.record_suggestion(
        playbook_id=req.playbook_id,
        text=req.text,
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
