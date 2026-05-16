"""Agent endpoints: classify a ticket, retrieve matching playbooks, draft a reply."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from core.classifier import classify_ticket
from core.drafter import draft_reply
from core.retrieval import (
    Playbook,
    PlaybookIndex,
    RetrievalHit,
    country_from_labels,
    detect_language,
    retrieve,
)

from ..deps import get_playbook_index, get_playbooks
from ..schemas import (
    ClassifyRequest,
    ClassifyResponse,
    DraftRequest,
    DraftResponse,
    RetrievalHitOut,
    RetrieveRequest,
    RetrieveResponse,
)
from ..serializers import derive_project_keys


router = APIRouter(prefix="/agent", tags=["agent"])


def _hit_to_out(hit: RetrievalHit) -> RetrievalHitOut:
    pb = hit.playbook
    meta = pb.metadata
    return RetrievalHitOut(
        playbook_id=pb.id,
        title=pb.title,
        description=pb.description,
        score=hit.score,
        rank=hit.rank,
        ticket_class=pb.ticket_class,
        issue_category=pb.issue_category,
        country_focus=pb.country_focus,
        languages=pb.languages,
        status=str(meta.get("status") or "active"),
        extraction_confidence=(
            float(meta["extraction_confidence"])
            if meta.get("extraction_confidence") is not None
            else None
        ),
        project_keys=derive_project_keys(list(meta.get("evidence_tickets") or [])),
    )


@router.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest) -> ClassifyResponse:
    try:
        result = classify_ticket(
            summary=req.summary,
            description=req.description,
            reporter_email=req.reporter_email,
            labels=req.labels,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Classifier failed: {exc}") from exc
    return ClassifyResponse(
        label=result.label,
        confidence=result.confidence,
        reason=result.reason,
    )


@router.post("/retrieve", response_model=RetrieveResponse)
def agent_retrieve(
    req: RetrieveRequest,
    request: Request,
) -> RetrieveResponse:
    index: PlaybookIndex = get_playbook_index(request)
    ticket_text = f"{req.summary}\n\n{req.description}".strip()
    if not ticket_text:
        raise HTTPException(status_code=422, detail="Empty ticket_text")

    hits = retrieve(
        index,
        ticket_text,
        labels=req.labels,
        ticket_class=req.ticket_class,
        top_k=req.top_k,
    )
    return RetrieveResponse(
        hits=[_hit_to_out(h) for h in hits],
        detected_language=detect_language(ticket_text),
        detected_country=country_from_labels(req.labels),
    )


@router.post("/draft", response_model=DraftResponse)
def agent_draft(
    req: DraftRequest,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> DraftResponse:
    playbook = next((pb for pb in playbooks if pb.id == req.playbook_id), None)
    if playbook is None:
        raise HTTPException(status_code=404, detail=f"Playbook {req.playbook_id!r} not found")

    try:
        result = draft_reply(
            ticket_summary=req.ticket_summary,
            ticket_description=req.ticket_description,
            playbook=playbook,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Drafter failed: {exc}") from exc

    return DraftResponse(
        draft=result.draft,
        recommended_action=result.recommended_action,
        rationale=result.rationale,
    )
