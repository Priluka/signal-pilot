"""Aggregate category counts for the sidebar."""
from __future__ import annotations

from collections import Counter, defaultdict

from fastapi import APIRouter, Depends

from core.retrieval import Playbook

from ..deps import get_playbooks
from ..schemas import CategoriesResponse, CountedName


router = APIRouter(tags=["categories"])


@router.get("/categories", response_model=CategoriesResponse)
def get_categories(
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> CategoriesResponse:
    ticket_class_counts: Counter[str] = Counter()
    issue_category_counts: Counter[str] = Counter()
    by_class: dict[str, Counter[str]] = defaultdict(Counter)

    for pb in playbooks:
        cls = pb.ticket_class or "uncategorized"
        cat = pb.issue_category or "other"
        ticket_class_counts[cls] += 1
        issue_category_counts[cat] += 1
        by_class[cls][cat] += 1

    return CategoriesResponse(
        total=len(playbooks),
        ticket_classes=[
            CountedName(name=name, count=count)
            for name, count in sorted(ticket_class_counts.items(), key=lambda x: (-x[1], x[0]))
        ],
        issue_categories=[
            CountedName(name=name, count=count)
            for name, count in sorted(issue_category_counts.items(), key=lambda x: (-x[1], x[0]))
        ],
        by_ticket_class={
            cls: [
                CountedName(name=name, count=count)
                for name, count in sorted(cats.items(), key=lambda x: (-x[1], x[0]))
            ]
            for cls, cats in by_class.items()
        },
    )
