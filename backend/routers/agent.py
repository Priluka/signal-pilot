"""Agent endpoints: classify a ticket, retrieve matching playbooks, draft a reply."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from core import agent_runner, agent_sessions
from core import suggestions as suggestions_store
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

from ..deps import get_playbook_index, get_playbooks, get_tickets
from ..schemas import (
    AgentActivityEvent,
    AgentMetrics,
    AgentSessionDetail,
    AgentSessionSummary,
    BatchStatus,
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
def classify(
    req: ClassifyRequest,
    ticket_id: str | None = Query(default=None, description="Persist under this ticket_id"),
) -> ClassifyResponse:
    try:
        result = classify_ticket(
            summary=req.summary,
            description=req.description,
            reporter_email=req.reporter_email,
            labels=req.labels,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Classifier failed: {exc}") from exc
    response = ClassifyResponse(
        label=result.label,
        confidence=result.confidence,
        reason=result.reason,
    )
    if ticket_id:
        try:
            agent_sessions.upsert_classification(ticket_id, response.model_dump())
        except Exception:
            pass
    return response


@router.post("/retrieve", response_model=RetrieveResponse)
def agent_retrieve(
    req: RetrieveRequest,
    request: Request,
    ticket_id: str | None = Query(default=None, description="Persist under this ticket_id"),
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
    response = RetrieveResponse(
        hits=[_hit_to_out(h) for h in hits],
        detected_language=detect_language(ticket_text),
        detected_country=country_from_labels(req.labels),
    )
    if ticket_id:
        try:
            agent_sessions.upsert_retrieval(ticket_id, response.model_dump())
        except Exception:
            pass
    return response


@router.post("/draft", response_model=DraftResponse)
def agent_draft(
    req: DraftRequest,
    ticket_id: str | None = Query(default=None, description="Persist under this ticket_id"),
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

    response = DraftResponse(
        draft=result.draft,
        recommended_action=result.recommended_action,
        rationale=result.rationale,
    )
    if ticket_id:
        try:
            agent_sessions.upsert_draft(ticket_id, req.playbook_id, response.model_dump())
        except Exception:
            pass
    return response


# ---------------------------------------------------------------------------
# Per-ticket workflow session (GET + DELETE for rehydration / redo)
# ---------------------------------------------------------------------------
def _record_to_detail(r: agent_sessions.AgentSessionRecord) -> AgentSessionDetail:
    return AgentSessionDetail(
        ticket_id=r.ticket_id,
        classification=ClassifyResponse(**r.classification) if r.classification else None,
        retrieval=RetrieveResponse(**r.retrieval) if r.retrieval else None,
        draft=DraftResponse(**r.draft) if r.draft else None,
        draft_playbook_id=r.draft_playbook_id,
        edited_text=r.edited_text,
        feedback_status=r.feedback_status,
        derived_status=agent_sessions.derive_status(r),
        updated_at=r.updated_at,
        started_at=r.started_at,
        classified_at=r.classified_at,
        retrieved_at=r.retrieved_at,
        drafted_at=r.drafted_at,
        feedback_at=r.feedback_at,
    )


def _record_to_summary(
    r: agent_sessions.AgentSessionRecord,
    playbook_title_by_id: dict[str, str],
) -> AgentSessionSummary:
    classification = r.classification or {}
    draft = r.draft or {}
    return AgentSessionSummary(
        ticket_id=r.ticket_id,
        derived_status=agent_sessions.derive_status(r),
        classification_label=classification.get("label"),
        classification_confidence=classification.get("confidence"),
        draft_playbook_id=r.draft_playbook_id,
        draft_playbook_title=(
            playbook_title_by_id.get(r.draft_playbook_id)
            if r.draft_playbook_id
            else None
        ),
        recommended_action=draft.get("recommended_action"),
        feedback_status=r.feedback_status,
        updated_at=r.updated_at,
        drafted_at=r.drafted_at,
        feedback_at=r.feedback_at,
    )


@router.get("/sessions", response_model=list[AgentSessionSummary])
def list_agent_sessions(
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> list[AgentSessionSummary]:
    titles = {pb.id: pb.title for pb in playbooks}
    return [
        _record_to_summary(r, titles)
        for r in agent_sessions.list_sessions()
    ]


# ---------------------------------------------------------------------------
# Batch processing (auto-fill the inbox in the background)
# ---------------------------------------------------------------------------
@router.post("/batch-process", response_model=BatchStatus)
def batch_process(
    request: Request,
    tickets: list[dict] = Depends(get_tickets),
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> BatchStatus:
    index = get_playbook_index(request)
    state = agent_runner.start_batch(tickets, playbooks, index)
    return BatchStatus(**state)


@router.get("/batch-status", response_model=BatchStatus)
def batch_status() -> BatchStatus:
    return BatchStatus(**agent_runner.get_batch_status())


@router.get("/activity", response_model=list[AgentActivityEvent])
def list_activity(limit: int = 500) -> list[AgentActivityEvent]:
    """Flatten every agent_session into one event per step + one per decision.
    Sorted newest-first so the frontend can append below without re-sorting."""
    events: list[AgentActivityEvent] = []
    for s in agent_sessions.list_sessions():
        classification = s.classification or {}
        retrieval = s.retrieval or {}
        draft = s.draft or {}

        if s.classified_at and classification:
            label = classification.get("label", "?")
            confidence = classification.get("confidence")
            conf_str = (
                f"{float(confidence):.2f}"
                if isinstance(confidence, (int, float))
                else "—"
            )
            if label in ("internal_log", "spam_or_junk"):
                events.append(
                    AgentActivityEvent(
                        timestamp=s.classified_at,
                        ticket_id=s.ticket_id,
                        event_type="skipped",
                        detail=f"{label} ({conf_str}) — no reply needed",
                    )
                )
            else:
                events.append(
                    AgentActivityEvent(
                        timestamp=s.classified_at,
                        ticket_id=s.ticket_id,
                        event_type="classified",
                        detail=f"{label} ({conf_str})",
                    )
                )

        if s.retrieved_at and retrieval:
            hits = retrieval.get("hits") or []
            top = hits[0] if hits else None
            if top:
                title = str(top.get("title") or "")[:60]
                score = top.get("score")
                score_str = (
                    f"{float(score):.2f}" if isinstance(score, (int, float)) else "—"
                )
                detail = (
                    f"{len(hits)} match{'es' if len(hits) != 1 else ''}, "
                    f"top: {title} ({score_str})"
                )
            else:
                detail = "0 matches"
            events.append(
                AgentActivityEvent(
                    timestamp=s.retrieved_at,
                    ticket_id=s.ticket_id,
                    event_type="retrieved",
                    detail=detail,
                )
            )

        if s.drafted_at and draft:
            action = str(draft.get("recommended_action") or "").replace("_", " ")
            events.append(
                AgentActivityEvent(
                    timestamp=s.drafted_at,
                    ticket_id=s.ticket_id,
                    event_type="drafted",
                    detail=f"recommended: {action}" if action else "draft generated",
                )
            )

        if s.feedback_at and s.feedback_status:
            label_map = {
                "approved": "Reviewer approved",
                "edited": "Reviewer approved with edits",
                "rejected": "Reviewer rejected",
            }
            events.append(
                AgentActivityEvent(
                    timestamp=s.feedback_at,
                    ticket_id=s.ticket_id,
                    event_type=s.feedback_status,
                    detail=label_map.get(s.feedback_status, s.feedback_status),
                )
            )

    # Suggestion lifecycle events — grouped under the playbook id so all
    # activity for a given playbook shows up together in the log.
    for sug in suggestions_store.list_suggestions():
        step_str = f" · Step {sug.step_number}" if sug.step_number is not None else ""
        section_str = sug.section.replace("_", " ")
        verb = {"edit": "edit", "add": "add", "remove": "remove"}.get(sug.type, sug.type)
        events.append(
            AgentActivityEvent(
                timestamp=sug.timestamp,
                ticket_id=sug.playbook_id,
                event_type="suggestion_created",
                detail=f"#{sug.id} {verb} · {section_str}{step_str} · by {sug.author}",
            )
        )
        if sug.status in ("accepted", "rejected") and sug.decided_at:
            events.append(
                AgentActivityEvent(
                    timestamp=sug.decided_at,
                    ticket_id=sug.playbook_id,
                    event_type=f"suggestion_{sug.status}",
                    detail=f"#{sug.id} {verb} · {section_str}{step_str}",
                )
            )

    events.sort(key=lambda e: e.timestamp, reverse=True)
    return events[:limit]


@router.get("/metrics", response_model=AgentMetrics)
def metrics(
    tickets: list[dict] = Depends(get_tickets),
) -> AgentMetrics:
    sessions = agent_sessions.list_sessions()
    counts = {
        "needs_review": 0,
        "auto_drafted": 0,
        "auto_resolved": 0,
        "escalated": 0,
        "skipped": 0,
        "approved": 0,
        "rejected": 0,
        "in_progress": 0,
        "pending": 0,
    }
    confidences: list[float] = []
    for s in sessions:
        st = agent_sessions.derive_status(s)
        if st in counts:
            counts[st] += 1
        if s.classification and "confidence" in s.classification:
            try:
                confidences.append(float(s.classification["confidence"]))
            except (TypeError, ValueError):
                pass

    approved_total = counts["approved"] + counts["rejected"]
    approval_rate = counts["approved"] / approved_total if approved_total else 0.0
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    return AgentMetrics(
        total=len(tickets),
        processed=len(sessions),
        **counts,
        approval_rate=approval_rate,
        avg_confidence=avg_conf,
    )


@router.get("/sessions/{ticket_id}", response_model=AgentSessionDetail | None)
def get_agent_session(ticket_id: str) -> AgentSessionDetail | None:
    record = agent_sessions.get_session(ticket_id)
    if record is None:
        return None
    return _record_to_detail(record)


@router.delete("/sessions/{ticket_id}", status_code=204)
def delete_agent_session(ticket_id: str) -> None:
    agent_sessions.delete_session(ticket_id)
