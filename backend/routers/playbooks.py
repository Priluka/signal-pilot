"""Playbook list + detail endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from core.retrieval import Playbook

from ..deps import get_playbooks
from ..schemas import PlaybookDetail, PlaybookSummary
from ..serializers import to_detail, to_summary


router = APIRouter(prefix="/playbooks", tags=["playbooks"])


def _matches(
    pb: Playbook,
    *,
    ticket_class: str | None,
    issue_category: str | None,
    country: str | None,
    language: str | None,
    q: str | None,
) -> bool:
    if ticket_class and pb.ticket_class != ticket_class:
        return False
    if issue_category and pb.issue_category != issue_category:
        return False
    if country and country not in pb.country_focus and "other" not in pb.country_focus:
        return False
    if language and language not in pb.languages and "other" not in pb.languages:
        return False
    if q:
        needle = q.lower()
        if needle not in pb.title.lower() and needle not in pb.description.lower():
            return False
    return True


@router.get("", response_model=list[PlaybookSummary])
def list_playbooks(
    ticket_class: str | None = Query(default=None),
    issue_category: str | None = Query(default=None),
    country: str | None = Query(default=None),
    language: str | None = Query(default=None),
    q: str | None = Query(default=None, description="Free-text match on title/description"),
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> list[PlaybookSummary]:
    filtered = [
        pb for pb in playbooks
        if _matches(
            pb,
            ticket_class=ticket_class,
            issue_category=issue_category,
            country=country,
            language=language,
            q=q,
        )
    ]
    filtered.sort(key=lambda pb: pb.title.lower())
    return [to_summary(pb) for pb in filtered]


@router.get("/{playbook_id}", response_model=PlaybookDetail)
def get_playbook(
    playbook_id: str,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> PlaybookDetail:
    for pb in playbooks:
        if pb.id == playbook_id:
            return to_detail(pb)
    raise HTTPException(status_code=404, detail=f"Playbook {playbook_id!r} not found")
