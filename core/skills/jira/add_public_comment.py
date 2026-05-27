"""Skill: ``jira_add_public_comment``.

Posts a public-facing reply to a Jira ticket — visible to the customer in
both Jira and the JSM portal. Always a HITL action: the operator reviews
the wording before send because this is what the customer reads.

Use cases: the drafted reply, follow-ups asking for more info, the final
"your refund has been processed" confirmation. For internal handoff
notes use ``jira_add_internal_comment`` instead.
"""
from __future__ import annotations

from typing import Any

from core import jira_client
from core.skills.base import Skill, SkillResult
from core.skills.registry import register


@register
class JiraAddPublicComment(Skill):
    name = "jira_add_public_comment"

    description = (
        "Post a public reply to a Jira ticket. THE CUSTOMER READS THIS. "
        "Use for sending the drafted answer, asking the customer for missing "
        "details, or confirming a resolution. Always HITL — the operator "
        "approves before send. For colleague-only notes use "
        "jira_add_internal_comment."
    )

    is_write = True

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "Jira issue key, e.g. 'KAN-34'.",
            },
            "body": {
                "type": "string",
                "description": (
                    "Reply text. Plain text, one paragraph per line. Match "
                    "the customer's language. Sign off appropriately for the "
                    "support team."
                ),
                "maxLength": 4000,
            },
        },
        "required": ["ticket_id", "body"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        ticket_id: str = params["ticket_id"]
        body: str = params["body"]

        try:
            response = jira_client.add_comment(ticket_id, body, internal=False)
        except jira_client.JiraConfigError as exc:
            return SkillResult(ok=False, error=f"jira_not_configured: {exc}")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(ok=False, error=f"jira_api_error: {exc}")

        return SkillResult(
            ok=True,
            data={
                "comment_id": str(response.get("id") or ""),
                "ticket_id": ticket_id,
                "body_sent": body,
            },
        )
