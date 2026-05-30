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

import json
from typing import Iterator

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from httpx import HTTPStatusError

from backend.deps import get_playbook_index, get_playbooks
from backend.schemas import (
    AgentSessionDetail,
    ClassifyResponse,
    DraftResponse,
    JiraCommentRequest,
    JiraCommentResponse,
    JiraConnectionStatus,
    JiraTicketDetail,
    JiraTicketSummary,
    RetrieveResponse,
)
from core import agent_config, agent_runner, agent_sessions, jira_client
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


def _sse(event: str, data: dict) -> str:
    """Format a single SSE frame. Same wire shape as the chat endpoint."""
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@router.post("/process/{issue_key}/stream")
def process_jira_ticket_stream(
    issue_key: str,
    request: Request,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> StreamingResponse:
    """Same pipeline as POST /process/{key}, but the response is an SSE
    stream: one event per milestone (classified, retrieved, drafted,
    planner_started, planner_done, done).

    The frontend feeds these into the timeline one at a time so the
    operator sees the work happening live instead of a 20-second wait
    followed by a sudden full page. The non-streaming endpoint above
    still exists for batch / scripted callers.
    """
    try:
        ticket = jira_client.get_ticket(issue_key)
    except JiraConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except HTTPStatusError as exc:
        raise _wrap_jira_error(exc) from exc

    index: PlaybookIndex = get_playbook_index(request)

    def _gen() -> Iterator[str]:
        try:
            for event in agent_runner.process_ticket_streaming(
                ticket, playbooks, index
            ):
                event_type = str(event.pop("type", "step"))
                yield _sse(event_type, event)
                if event_type == "done":
                    # Post-stream side effects: mode-aware auto-post.
                    # Mirror the blocking endpoint so behaviour matches.
                    record = agent_sessions.get_session(issue_key)
                    if record is not None:
                        _maybe_auto_post(issue_key, record)
        except Exception as exc:  # noqa: BLE001
            yield _sse("error", {"step": "stream", "message": str(exc)})

    return StreamingResponse(
        _gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/process/{issue_key}", response_model=AgentSessionDetail)
def process_jira_ticket(
    issue_key: str,
    request: Request,
    playbooks: list[Playbook] = Depends(get_playbooks),
) -> AgentSessionDetail:
    """Run classify → retrieve → draft on a Jira ticket and return the
    resulting agent session. Session is keyed by the Jira issue key, so it
    shows up in /agent/sessions/{issue_key} like any local ticket.

    After the agent finishes, the active mode (effective per-playbook) plus
    confidence threshold decide whether a comment is also posted to Jira:

    * shadow      — never write
    * assisted    — write a clearly-marked DRAFT comment so the operator
                    can review it on the Jira side
    * autonomous  — post the draft AS THE FINAL REPLY only when the
                    classifier confidence ≥ threshold; below threshold,
                    fall back to assisted behaviour so a human still sees
                    the candidate before it ships.
    """
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

    # Mode-aware auto-post: only when we actually drafted something.
    _maybe_auto_post(issue_key, record)

    record = agent_sessions.get_session(issue_key) or record
    import os

    base = (os.environ.get("JIRA_URL") or "").rstrip("/")
    jira_url = f"{base}/browse/{issue_key}" if base else None
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
        auto_posted_at=record.auto_posted_at,
        processed_mode=record.processed_mode,
        jira_browse_url=jira_url,
        planner_status=record.planner_status,
        planner_error=record.planner_error,
        planner_updated_at=record.planner_updated_at,
        routing=record.routing,
        error_step=record.error_step,
        error_message=record.error_message,
    )


def _maybe_auto_post(issue_key: str, record) -> None:
    """Post a clean Jira comment ONLY in autonomous mode when classifier
    confidence cleared the threshold. Everything else — shadow, assisted,
    autonomous-below-threshold — leaves Jira untouched until the operator
    explicitly approves from the inbox.

    The customer must never see a [DRAFT] marker. Drafts live only in our
    UI; Approve in the inbox is what posts them as the final reply.
    """
    if not record.draft:
        return
    draft_text = (record.draft or {}).get("draft") or ""
    if not draft_text.strip():
        return

    effective = agent_config.effective_mode(record.draft_playbook_id)
    if effective != "autonomous":
        return

    threshold = agent_config.get_confidence_threshold()
    classification = record.classification or {}
    confidence = float(classification.get("confidence") or 0.0)
    if confidence < threshold:
        # Below threshold → falls back to assisted behaviour, which means
        # the operator decides via the inbox. No auto-post.
        return

    try:
        jira_client.add_comment(issue_key, draft_text)
    except Exception as exc:  # noqa: BLE001
        log.warning("Auto-post to Jira failed for %s: %s", issue_key, exc)
        return

    try:
        agent_sessions.upsert_feedback(issue_key, "approved", edited_text=None)
    except Exception as exc:  # noqa: BLE001
        log.warning("Could not mark %s auto-approved: %s", issue_key, exc)

    try:
        agent_sessions.mark_auto_posted(issue_key)
    except Exception as exc:  # noqa: BLE001
        log.warning("Could not stamp auto_posted_at for %s: %s", issue_key, exc)


@router.get("/connection", response_model=JiraConnectionStatus)
def jira_connection_status(probe: bool = False) -> JiraConnectionStatus:
    """Surface Jira credentials shape (masked) and, optionally, a live ping.

    ``probe=true`` hits ``/rest/api/3/myself`` once — used by the Test
    connection button in the Agents page. Default is metadata-only so
    page loads don't ping Atlassian.
    """
    import os

    url = os.environ.get("JIRA_URL") or None
    email = os.environ.get("JIRA_EMAIL") or None
    project = os.environ.get("JIRA_PROJECT") or None
    token = os.environ.get("JIRA_TOKEN") or ""
    configured = bool(url and email and token and project)
    token_masked = None
    if token:
        # Show first 6 + last 4 so operator can tell which token is wired
        # in without being able to copy the full secret from the UI.
        token_masked = f"{token[:6]}…{token[-4:]}" if len(token) > 12 else "(set)"
    status = JiraConnectionStatus(
        configured=configured,
        url=url,
        email=email,
        project=project,
        token_masked=token_masked,
    )
    if not probe or not configured:
        return status
    try:
        from core.jira_client import _client  # type: ignore[attr-defined]

        with _client() as c:
            r = c.get("/rest/api/3/myself")
            r.raise_for_status()
            body = r.json()
        status.reachable = True
        status.detail = f"OK · authenticated as {body.get('displayName')}"
    except JiraConfigError as exc:
        status.reachable = False
        status.detail = str(exc)
    except HTTPStatusError as exc:
        status.reachable = False
        status.detail = f"{exc.response.status_code} {exc.response.reason_phrase}"
    except Exception as exc:  # noqa: BLE001
        status.reachable = False
        status.detail = f"{type(exc).__name__}: {exc}"
    return status


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


