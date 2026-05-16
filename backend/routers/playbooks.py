"""Playbook list + detail endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from core.retrieval import Playbook

from ..deps import get_playbooks
from ..schemas import GraphEdge, GraphNode, GraphResponse, PlaybookDetail, PlaybookSummary
from ..serializers import to_detail, to_summary


router = APIRouter(prefix="/playbooks", tags=["playbooks"])


def _opt_float(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _opt_int(value):
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


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


@router.get("/graph", response_model=GraphResponse)
def get_graph(
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> GraphResponse:
    """Force-directed graph of the playbook corpus.

    Nodes are playbooks; edges are ``related_playbooks`` cross-references.
    The list is deduped to undirected pairs so each conceptual link appears
    once. ``degree`` is precomputed per node so the frontend doesn't need a
    second pass to size them.
    """
    by_id = {pb.id: pb for pb in playbooks}
    seen_edges: set[tuple[str, str]] = set()
    degrees: dict[str, int] = {pb.id: 0 for pb in playbooks}

    edges: list[GraphEdge] = []
    for pb in playbooks:
        related = pb.metadata.get("related_playbooks") or []
        for raw in related:
            target = str(raw)
            if target not in by_id or target == pb.id:
                continue
            key = tuple(sorted([pb.id, target]))
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append(GraphEdge(source=key[0], target=key[1]))
            degrees[key[0]] += 1
            degrees[key[1]] += 1

    nodes = [
        GraphNode(
            id=pb.id,
            title=pb.title,
            ticket_class=pb.ticket_class,
            issue_category=pb.issue_category,
            cluster_size=_opt_int(pb.metadata.get("cluster_size")),
            extraction_confidence=_opt_float(pb.metadata.get("extraction_confidence")),
            status=str(pb.metadata.get("status") or "active"),
            degree=degrees[pb.id],
        )
        for pb in playbooks
    ]
    return GraphResponse(nodes=nodes, edges=edges)


@router.get("/{playbook_id}", response_model=PlaybookDetail)
def get_playbook(
    playbook_id: str,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> PlaybookDetail:
    for pb in playbooks:
        if pb.id == playbook_id:
            return to_detail(pb)
    raise HTTPException(status_code=404, detail=f"Playbook {playbook_id!r} not found")
