"""Jira REST proxy: list project tickets and post comments.

Credentials come from the environment (``JIRA_URL``, ``JIRA_EMAIL``,
``JIRA_TOKEN``, ``JIRA_PROJECT``) and are read inside ``core.jira_client``
on each call, so changes to ``.env`` take effect on the next request without
a restart of the import graph.

Endpoints run on the FastAPI threadpool (sync funcs) because the underlying
``httpx.Client`` calls are blocking — keeps the async event loop free.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from httpx import HTTPStatusError

from backend.deps import get_playbook_index, get_playbooks
from backend.schemas import (
    AgentSessionDetail,
    ClassifyResponse,
    DraftResponse,
    JiraCommentRequest,
    JiraCommentResponse,
    JiraTicketDetail,
    JiraTicketSummary,
    RetrieveResponse,
)
from core import agent_runner, agent_sessions, jira_client
from core.jira_client import JiraConfigError
from core.retrieval import Playbook, PlaybookIndex


router = APIRouter(prefix="/jira", tags=["jira"])
log = logging.getLogger(__name__)


def _wrap_jira_error(exc: HTTPStatusError) -> HTTPException:
    """Surface Jira's status code + first error message to the client."""
    status = exc.response.status_code
    try:
        body = exc.response.json()
        msg = (
            body.get("errorMessages", [None])[0]
            or next(iter((body.get("errors") or {}).values()), None)
            or str(body)
        )
    except Exception:
        msg = exc.response.text or str(exc)
    return HTTPException(status_code=status, detail=f"Jira: {msg}")


@router.get("/tickets", response_model=list[JiraTicketSummary])
def list_jira_tickets(limit: int = 100) -> list[JiraTicketSummary]:
    try:
        rows = jira_client.list_tickets(max_results=limit)
    except JiraConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPStatusError as exc:
        raise _wrap_jira_error(exc) from exc
    return [JiraTicketSummary(**r) for r in rows]


@router.get("/tickets/{issue_key}", response_model=JiraTicketDetail)
def get_jira_ticket(issue_key: str) -> JiraTicketDetail:
    try:
        row = jira_client.get_ticket(issue_key)
    except JiraConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPStatusError as exc:
        raise _wrap_jira_error(exc) from exc
    return JiraTicketDetail(**row)


@router.post("/process/{issue_key}", response_model=AgentSessionDetail)
def process_jira_ticket(
    issue_key: str,
    request: Request,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> AgentSessionDetail:
    """Run classify → retrieve → draft on a Jira ticket and return the
    resulting agent session. Session is keyed by the Jira issue key, so it
    shows up in /agent/sessions/{issue_key} like any local ticket."""
    try:
        ticket = jira_client.get_ticket(issue_key)
    except JiraConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPStatusError as exc:
        raise _wrap_jira_error(exc) from exc

    index: PlaybookIndex = get_playbook_index(request)
    agent_runner.process_ticket(ticket, playbooks, index)

    record = agent_sessions.get_session(issue_key)
    if record is None:
        raise HTTPException(
            status_code=500, detail="Agent ran but no session was persisted"
        )
    return AgentSessionDetail(
        ticket_id=record.ticket_id,
        classification=ClassifyResponse(**record.classification) if record.classification else None,
        retrieval=RetrieveResponse(**record.retrieval) if record.retrieval else None,
        draft=DraftResponse(**record.draft) if record.draft else None,
        draft_playbook_id=record.draft_playbook_id,
        edited_text=record.edited_text,
        feedback_status=record.feedback_status,
        derived_status=agent_sessions.derive_status(record),
        updated_at=record.updated_at,
        started_at=record.started_at,
        classified_at=record.classified_at,
        retrieved_at=record.retrieved_at,
        drafted_at=record.drafted_at,
        feedback_at=record.feedback_at,
    )


@router.post("/comment", response_model=JiraCommentResponse)
def post_jira_comment(req: JiraCommentRequest) -> JiraCommentResponse:
    if not req.body.strip():
        raise HTTPException(status_code=400, detail="Comment body is empty")
    try:
        resp = jira_client.add_comment(req.issue_key, req.body)
    except JiraConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPStatusError as exc:
        raise _wrap_jira_error(exc) from exc
    author = (resp.get("author") or {}).get("displayName")
    return JiraCommentResponse(
        id=str(resp.get("id") or ""),
        issue_key=req.issue_key,
        created=resp.get("created"),
        author=author,
    )
