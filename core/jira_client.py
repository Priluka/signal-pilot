"""Thin wrapper around the Jira REST v3 API.

Reads ``JIRA_URL``, ``JIRA_EMAIL``, ``JIRA_TOKEN``, ``JIRA_PROJECT`` from the
environment (loaded via ``.env``). All requests use HTTP Basic auth with
email + API token — the standard Atlassian Cloud pattern.

Description fields and comment bodies use Atlassian Document Format (ADF);
``_adf_to_text`` flattens ADF to plain text for display, and ``_text_to_adf``
wraps an outgoing comment string in the minimal ADF envelope Jira expects.
"""
from __future__ import annotations

import os
from typing import Any

import httpx


class JiraConfigError(RuntimeError):
    """Raised when required Jira env vars are missing."""


def _config() -> tuple[str, str, str, str]:
    url = os.environ.get("JIRA_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_TOKEN", "")
    project = os.environ.get("JIRA_PROJECT", "")
    if not (url and email and token and project):
        raise JiraConfigError(
            "Jira not configured — set JIRA_URL, JIRA_EMAIL, JIRA_TOKEN, JIRA_PROJECT in .env"
        )
    return url, email, token, project


def _client() -> httpx.Client:
    url, email, token, _ = _config()
    return httpx.Client(
        base_url=url,
        auth=(email, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        timeout=30.0,
    )


def project_key() -> str:
    return _config()[3]


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def list_tickets(max_results: int = 100) -> list[dict[str, Any]]:
    """Return tickets from the configured project, newest first.

    Uses the new ``/rest/api/3/search/jql`` endpoint (the legacy ``/search``
    is being deprecated). Only requests the fields the Inbox needs.
    """
    _, _, _, project = _config()
    fields = [
        "summary",
        "description",
        "status",
        "priority",
        "labels",
        "reporter",
        "assignee",
        "issuetype",
        "resolution",
        "resolutiondate",
        "created",
        "comment",
    ]
    params = {
        "jql": f"project={project} ORDER BY created DESC",
        "maxResults": str(max_results),
        "fields": ",".join(fields),
    }
    with _client() as c:
        r = c.get("/rest/api/3/search/jql", params=params)
        r.raise_for_status()
        body = r.json()
    return [_summarize_issue(it) for it in body.get("issues", [])]


def get_ticket(issue_key: str) -> dict[str, Any]:
    """Return one ticket as a TicketDetail-shaped dict."""
    fields = [
        "summary",
        "description",
        "status",
        "priority",
        "labels",
        "reporter",
        "assignee",
        "issuetype",
        "resolution",
        "resolutiondate",
        "created",
        "project",
        "comment",
    ]
    with _client() as c:
        r = c.get(
            f"/rest/api/3/issue/{issue_key}",
            params={"fields": ",".join(fields)},
        )
        r.raise_for_status()
        issue = r.json()
    return _detail_issue(issue)


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------

def add_comment(
    issue_key: str,
    body_text: str,
    *,
    internal: bool = False,
) -> dict[str, Any]:
    """Post a plain-text comment to ``issue_key``. Returns the Jira response.

    When ``internal=True`` the comment is tagged with the JSM
    ``sd.public.comment`` property so it stays hidden from the customer
    portal. On non-JSM projects the property is silently ignored — the
    comment posts as normal.
    """
    payload: dict[str, Any] = {"body": _text_to_adf(body_text)}
    if internal:
        payload["properties"] = [
            {"key": "sd.public.comment", "value": {"internal": True}}
        ]
    with _client() as c:
        r = c.post(f"/rest/api/3/issue/{issue_key}/comment", json=payload)
        r.raise_for_status()
        return r.json()


def list_comments(
    issue_key: str,
    max_results: int = 50,
) -> list[dict[str, Any]]:
    """Return comments on ``issue_key`` oldest-first.

    Each entry is ``{id, author, created, body, internal}`` — body is
    flattened to plain text via ``_adf_to_text``, internal is detected
    from the JSM ``sd.public.comment`` property when present.
    """
    with _client() as c:
        r = c.get(
            f"/rest/api/3/issue/{issue_key}/comment",
            params={"maxResults": str(max_results), "orderBy": "created"},
        )
        r.raise_for_status()
        data = r.json()
    out: list[dict[str, Any]] = []
    for comment in data.get("comments", []) or []:
        author = comment.get("author") or {}
        internal = False
        for prop in comment.get("properties") or []:
            if prop.get("key") == "sd.public.comment":
                internal = bool((prop.get("value") or {}).get("internal"))
                break
        out.append(
            {
                "id": comment.get("id"),
                "author": author.get("displayName") or author.get("emailAddress") or "",
                "created": comment.get("created"),
                "body": _adf_to_text(comment.get("body")).strip(),
                "internal": internal,
            }
        )
    return out


def get_transitions(issue_key: str) -> list[dict[str, Any]]:
    """List transitions currently valid for ``issue_key``.

    Each entry is ``{id, name, to_name}`` — ``to_name`` is the status
    the transition lands on, which is what callers usually want to
    match against.
    """
    with _client() as c:
        r = c.get(f"/rest/api/3/issue/{issue_key}/transitions")
        r.raise_for_status()
        data = r.json()
    out: list[dict[str, Any]] = []
    for t in data.get("transitions", []) or []:
        to = t.get("to") or {}
        out.append({"id": t.get("id"), "name": t.get("name"), "to_name": to.get("name")})
    return out


def transition(issue_key: str, target_status: str) -> dict[str, Any]:
    """Apply the transition that lands ``issue_key`` on ``target_status``.

    Looks up valid transitions, picks the one whose ``to_name`` matches
    (case-insensitive). Raises ``ValueError`` if no such transition is
    available — the planner surfaces this as a failed skill result so
    Claude can pick a different action.
    """
    transitions = get_transitions(issue_key)
    norm = target_status.strip().lower()
    match = next(
        (t for t in transitions if (t["to_name"] or "").lower() == norm),
        None,
    )
    if match is None:
        available = [t["to_name"] for t in transitions if t["to_name"]]
        raise ValueError(
            f"No transition to {target_status!r} available "
            f"(have: {available})"
        )
    payload = {"transition": {"id": match["id"]}}
    with _client() as c:
        r = c.post(f"/rest/api/3/issue/{issue_key}/transitions", json=payload)
        r.raise_for_status()
    return {"applied": match["to_name"], "transition_id": match["id"]}


# ---------------------------------------------------------------------------
# Issue → dict shaping
# ---------------------------------------------------------------------------

def _summarize_issue(issue: dict[str, Any]) -> dict[str, Any]:
    f = issue.get("fields") or {}
    reporter = f.get("reporter") or {}
    status = f.get("status") or {}
    priority = f.get("priority") or {}
    status_cat = (status.get("statusCategory") or {}).get("key")
    return {
        "key": issue.get("key"),
        "summary": f.get("summary") or "",
        "status": status.get("name") or "",
        "status_category": status_cat,
        "priority": priority.get("name"),
        "labels": list(f.get("labels") or []),
        "reporter_email": reporter.get("emailAddress"),
        "reporter_name": reporter.get("displayName"),
        "created_at": f.get("created"),
        "resolved_at": f.get("resolutiondate"),
    }


def _detail_issue(issue: dict[str, Any]) -> dict[str, Any]:
    base = _summarize_issue(issue)
    f = issue.get("fields") or {}
    assignee = f.get("assignee") or {}
    issuetype = f.get("issuetype") or {}
    resolution = f.get("resolution") or {}
    project = f.get("project") or {}
    comment_block = f.get("comment") or {}
    base.update(
        {
            "description": _adf_to_text(f.get("description")),
            "assignee_name": assignee.get("displayName"),
            "project_key": project.get("key"),
            "issue_type": issuetype.get("name"),
            "resolution": resolution.get("name"),
            "resolution_minutes": None,
            "comment_count_total": int(comment_block.get("total") or 0),
        }
    )
    return base


# ---------------------------------------------------------------------------
# ADF helpers
# ---------------------------------------------------------------------------

def _text_to_adf(text: str) -> dict[str, Any]:
    """Wrap a plain string in the minimal ADF doc Jira accepts for comments.

    Each line becomes its own paragraph so newlines render correctly.
    """
    lines = text.split("\n") if text else [""]
    content = [
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": line}] if line else [],
        }
        for line in lines
    ]
    return {"type": "doc", "version": 1, "content": content}


def _adf_to_text(node: Any) -> str:
    """Flatten an ADF node tree to plain text. Best-effort; ignores marks."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_adf_to_text(n) for n in node)
    if not isinstance(node, dict):
        return ""
    kind = node.get("type")
    if kind == "text":
        return node.get("text") or ""
    if kind == "hardBreak":
        return "\n"
    children = _adf_to_text(node.get("content"))
    if kind in {"paragraph", "heading", "listItem", "blockquote"}:
        return children + "\n"
    if kind in {"bulletList", "orderedList"}:
        return children
    return children
