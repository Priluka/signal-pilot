"""Skill: ``jira_get_history``.

Read-only fetch of every comment + current status on a Jira ticket. This
is the agent's "look before you act" tool — Claude calls this first to
build context (what's already been said to the customer, who the last
responder was, what the ticket status currently is) before deciding what
write action to take.

No side effects, safe to auto-execute in every mode.
"""
from __future__ import annotations

from typing import Any

from core import jira_client
from core.skills.base import Skill, SkillResult
from core.skills.registry import register


@register
class JiraGetHistory(Skill):
    name = "jira_get_history"

    description = (
        "Fetch the full comment history and current status of a Jira ticket. "
        "Returns comments oldest-first with author, timestamp, body text, and "
        "an internal/public flag, plus the ticket's current status. Read-only "
        "— use this to understand context before deciding what action to take."
    )

    is_write = False

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "Jira issue key, e.g. 'BS-45949' or 'KAN-34'.",
            },
        },
        "required": ["ticket_id"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        ticket_id: str = params["ticket_id"]
        try:
            ticket = jira_client.get_ticket(ticket_id)
            comments = jira_client.list_comments(ticket_id)
        except jira_client.JiraConfigError as exc:
            return SkillResult(ok=False, error=f"jira_not_configured: {exc}")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(ok=False, error=f"jira_api_error: {exc}")

        return SkillResult(
            ok=True,
            data={
                "ticket_id": ticket_id,
                "status": ticket.get("status") or "",
                "summary": ticket.get("summary") or "",
                "reporter": ticket.get("reporter_name") or "",
                "comment_count": len(comments),
                "comments": comments,
            },
        )
