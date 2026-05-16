"""Convert ``core.retrieval.Playbook`` instances into API response models."""
from __future__ import annotations

import re
from typing import Any

from core.retrieval import Playbook, extract_section

from .schemas import EvidenceQuote, PlaybookDetail, PlaybookSummary, TicketActionRow


# Numbered "1. step text" lines inside the resolution flow.
_NUMBERED_STEP_RE = re.compile(r"^\s*\d+\.\s+(?P<step>.+?)\s*$", re.MULTILINE)

# Evidence bullets:
#   - `BS-6340` _[other]_: "Platba vo výške 0,75..."
#   - `BS-7962` _[en]_: "Payment do fails regularly..."
_EVIDENCE_QUOTE_RE = re.compile(
    r"^- `(?P<id>[A-Z][A-Z0-9]*-\d+)`(?:\s+_\[(?P<lang>[^\]]+)\]_)?:\s+\"(?P<quote>.+?)\"\s*$",
    re.MULTILINE,
)

# Markdown table separator like "|---|---|"
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def derive_project_keys(evidence_tickets: list[str]) -> list[str]:
    """Pull unique project prefixes (BS, RAOS, ...) out of a list of Jira ticket IDs."""
    keys: set[str] = set()
    for ticket in evidence_tickets:
        if "-" in ticket:
            prefix = ticket.split("-", 1)[0]
            if prefix and prefix.isupper():
                keys.add(prefix)
    return sorted(keys)


def parse_resolution_steps(resolution_flow_md: str) -> list[str]:
    return [m.group("step").strip() for m in _NUMBERED_STEP_RE.finditer(resolution_flow_md)]


def parse_actions_table(actions_md: str) -> list[TicketActionRow]:
    """Parse a 4-column markdown table | What | Who | Tool | Duration |."""
    if not actions_md.strip():
        return []
    rows: list[TicketActionRow] = []
    table_lines = [
        line for line in actions_md.splitlines()
        if line.strip().startswith("|") and not _TABLE_SEPARATOR_RE.match(line)
    ]
    # First table row is the header; everything after is data.
    for line in table_lines[1:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4:
            rows.append(
                TicketActionRow(
                    what=cells[0],
                    who=cells[1],
                    tool=cells[2],
                    duration=cells[3],
                )
            )
    return rows


def parse_evidence_quotes(body: str) -> list[EvidenceQuote]:
    evidence_md = extract_section(body, "Evidence")
    if not evidence_md:
        return []
    return [
        EvidenceQuote(
            ticket_id=m.group("id"),
            language=m.group("lang"),
            quote=m.group("quote"),
        )
        for m in _EVIDENCE_QUOTE_RE.finditer(evidence_md)
    ]


def _opt_float(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _opt_int(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def to_summary(pb: Playbook) -> PlaybookSummary:
    meta = pb.metadata
    return PlaybookSummary(
        id=pb.id,
        title=pb.title,
        description=pb.description,
        category=pb.category,
        ticket_class=pb.ticket_class,
        issue_category=pb.issue_category,
        languages=pb.languages,
        country_focus=pb.country_focus,
        resolution_pattern=pb.resolution_pattern,
        status=str(meta.get("status") or "active"),
        extraction_confidence=_opt_float(meta.get("extraction_confidence")),
        cluster_size=_opt_int(meta.get("cluster_size")),
        project_keys=derive_project_keys(_as_str_list(meta.get("evidence_tickets"))),
    )


def to_detail(pb: Playbook) -> PlaybookDetail:
    meta = pb.metadata
    summary = to_summary(pb)
    return PlaybookDetail(
        **summary.model_dump(),
        when_applies=pb.when_applies,
        resolution_flow=pb.resolution_flow,
        typical_actions=pb.typical_actions,
        typical_actions_rows=parse_actions_table(pb.typical_actions),
        risks=pb.risks,
        body=pb.body,
        resolution_steps=parse_resolution_steps(pb.resolution_flow),
        evidence_tickets=_as_str_list(meta.get("evidence_tickets")),
        evidence_quotes=parse_evidence_quotes(pb.body),
        canonical_examples=_as_str_list(meta.get("canonical_examples")),
        related_playbooks=_as_str_list(meta.get("related_playbooks")),
        created=str(meta.get("created")) if meta.get("created") else None,
        updated=str(meta.get("updated")) if meta.get("updated") else None,
        correction_count=int(meta.get("correction_count") or 0),
        frequency_per_month=_opt_float(meta.get("frequency_per_month")),
        median_resolution_minutes=_opt_float(meta.get("median_resolution_minutes")),
        cluster_id=str(meta.get("cluster_id")) if meta.get("cluster_id") else None,
        metadata=meta,
    )
