"""Aggregate report over the playbook corpus — powers the /discovery view.

One pass over the in-memory playbook list builds: per-category counts,
country/language coverage, summed ROI hours, the five biggest patterns,
and a list of thin-coverage gaps. All numbers come from YAML frontmatter
that the loader already parsed at startup; nothing here re-reads disk.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from fastapi import APIRouter, Depends

from core.retrieval import Playbook

from ..deps import get_playbooks
from ..schemas import (
    CountedName,
    DiscoveryCategoryEntry,
    DiscoveryCountryEntry,
    DiscoveryGap,
    DiscoveryQuality,
    DiscoveryROISummary,
    DiscoveryReport,
    DiscoveryTopPlaybook,
)


router = APIRouter(prefix="/discovery", tags=["discovery"])


def _as_float(v: Any) -> float | None:
    if isinstance(v, (int, float)):
        return float(v)
    return None


def _as_int(v: Any) -> int:
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    return 0


@router.get("/report", response_model=DiscoveryReport)
def discovery_report(
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> DiscoveryReport:
    cat_counts: Counter[str] = Counter()
    cat_titles: dict[str, list[str]] = defaultdict(list)
    country_counts: Counter[str] = Counter()
    lang_counts: Counter[str] = Counter()
    confidences: list[float] = []
    total_tickets = 0
    baseline_sum = 0.0
    agent_assist_sum = 0.0
    autonomous_sum = 0.0

    for pb in playbooks:
        meta = pb.metadata or {}

        cs = _as_int(meta.get("cluster_size"))
        total_tickets += cs

        ec = _as_float(meta.get("extraction_confidence"))
        if ec is not None:
            confidences.append(ec)

        cat = pb.issue_category or "other"
        cat_counts[cat] += 1
        cat_titles[cat].append(pb.title)

        for c in pb.country_focus:
            if c and c != "other":
                country_counts[c] += 1
        for lang in pb.languages:
            if lang and lang != "other":
                lang_counts[lang] += 1

        roi = meta.get("roi")
        if isinstance(roi, dict):
            baseline_sum += _as_float(roi.get("baseline_active_hours")) or 0.0
            agent_assist_sum += _as_float(roi.get("agent_assist_hours_midpoint")) or 0.0
            autonomous_sum += _as_float(roi.get("autonomous_resolve_hours_midpoint")) or 0.0

    avg_conf = sum(confidences) / len(confidences) if confidences else None
    min_conf = min(confidences) if confidences else None
    max_conf = max(confidences) if confidences else None
    low_count = sum(1 for c in confidences if c < 0.75)

    gaps = sorted(
        (
            DiscoveryGap(category=name, count=cnt)
            for name, cnt in cat_counts.items()
            if cnt < 3
        ),
        key=lambda g: (g.count, g.category),
    )

    top = sorted(
        playbooks,
        key=lambda p: _as_int((p.metadata or {}).get("cluster_size")),
        reverse=True,
    )[:5]

    return DiscoveryReport(
        total_playbooks=len(playbooks),
        total_tickets_covered=total_tickets,
        avg_confidence=avg_conf,
        categories=[
            DiscoveryCategoryEntry(
                name=name,
                count=cnt,
                playbook_titles=cat_titles[name],
            )
            for name, cnt in sorted(cat_counts.items(), key=lambda x: (-x[1], x[0]))
        ],
        countries=[
            DiscoveryCountryEntry(code=code, count=cnt)
            for code, cnt in sorted(country_counts.items(), key=lambda x: (-x[1], x[0]))
        ],
        languages=[
            CountedName(name=name, count=cnt)
            for name, cnt in sorted(lang_counts.items(), key=lambda x: (-x[1], x[0]))
        ],
        roi_summary=DiscoveryROISummary(
            baseline_hours=baseline_sum,
            agent_assist_hours=agent_assist_sum,
            autonomous_hours=autonomous_sum,
        ),
        gaps=gaps,
        top_playbooks=[
            DiscoveryTopPlaybook(
                id=pb.id,
                title=pb.title,
                cluster_size=_as_int((pb.metadata or {}).get("cluster_size")),
            )
            for pb in top
        ],
        quality=DiscoveryQuality(
            min=min_conf,
            max=max_conf,
            avg=avg_conf,
            low_confidence_count=low_count,
        ),
    )
