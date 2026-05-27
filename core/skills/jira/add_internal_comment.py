"""Skill: ``jira_add_internal_comment``.

Adds an internal note to a Jira ticket. Internal notes are NOT visible to
the customer — they live in the "internal" comment visibility group and
are seen only by support staff with access to the project.

This is a write skill, but considered low-risk (no customer-facing impact,
no financial side effect, easily reversible by deleting the comment). The
playbook decides via its bullet's ``human_approval_required`` flag whether
this should still be HITL or can auto-execute.

Common use cases:
- Tagging a payment colleague with refund details ("@Lidija povrat 11.90 €")
- Recording handoff context for the next agent
- Marking that an automated action was taken ("Receipt sent at ...")
"""
from __future__ import annotations

from typing import Any

from core import jira_client
from core.skills.base import Skill, SkillResult
from core.skills.registry import register


@register
class JiraAddInternalComment(Skill):
    name = "jira_add_internal_comment"

    description = (
        "Add an internal-visibility note to a Jira ticket. NOT visible to the "
        "customer. Use for tagging a colleague, recording handoff context, or "
        "logging that an automated step was taken. The body should be a short "
        "plain-text message; mention a colleague by prefixing their name with @."
    )

    is_write = True

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "Jira issue key, e.g. 'BS-45949'.",
            },
            "body": {
                "type": "string",
                "description": (
                    "Comment text. Plain text, no markdown. Keep under 500 "
                    "characters. Reference colleagues with '@Name'."
                ),
                "maxLength": 500,
            },
            "mention": {
                "type": "string",
                "description": (
                    "Optional colleague name to @-mention. Will be prepended "
                    "to the body if provided."
                ),
            },
        },
        "required": ["ticket_id", "body"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        ticket_id: str = params["ticket_id"]
        body: str = params["body"]
        mention: str | None = params.get("mention")

        text = f"@{mention} {body}" if mention else body

        try:
            response = jira_client.add_comment(ticket_id, text)
        except jira_client.JiraConfigError as exc:
            return SkillResult(ok=False, error=f"jira_not_configured: {exc}")
        except Exception as exc:  # noqa: BLE001
            return SkillResult(ok=False, error=f"jira_api_error: {exc}")

        return SkillResult(
            ok=True,
            data={
                "comment_id": str(response.get("id") or ""),
                "ticket_id": ticket_id,
                "body_sent": text,
            },
        )
