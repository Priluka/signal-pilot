"""Skill: ``jira_transition``.

Move a Jira ticket from its current status to a different one. Wraps
``jira_client.transition`` which resolves a target-status name to the
matching workflow transition id.

Always HITL for terminal states (Resolved / Closed) — the planner's
validator enforces that based on the playbook's ``agent_compatibility``
flags. For intermediate states (In Progress, Waiting for vendor, …) a
playbook may opt-in to auto-execute in autonomous mode.
"""
from __future__ import annotations

from typing import Any

from core import jira_client
from core.skills.base import Skill, SkillResult
from core.skills.registry import register


# Status names accepted by the schema. Listed centrally so frontend +
# validator can reuse without re-defining the enum.
ALLOWED_TARGET_STATUSES: tuple[str, ...] = (
    "Open",
    "To Do",
    "In Progress",
    "Waiting for customer",
    "Waiting for vendor",
    "Resolved",
    "Closed",
    "Done",
)


@register
class JiraTransition(Skill):
    name = "jira_transition"

    description = (
        "Move a Jira ticket to a different status. Pick from the standard "
        "workflow states (In Progress, Waiting for customer, Resolved, …). "
        "If the target state is not reachable from the current state the "
        "skill fails — Claude should retry with a valid status."
    )

    is_write = True

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "Jira issue key, e.g. 'KAN-34'.",
            },
            "target_status": {
                "type": "string",
                "description": "Target status name (must match a valid transition).",
                "enum": list(ALLOWED_TARGET_STATUSES),
            },
        },
        "required": ["ticket_id", "target_status"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        ticket_id: str = params["ticket_id"]
        target: str = params["target_status"]

        try:
            applied = jira_client.transition(ticket_id, target)
        except jira_client.JiraConfigError as exc:
            return SkillResult(ok=False, error=f"jira_not_configured: {exc}")
        except ValueError as exc:
            # Most common case: workflow doesn't allow that transition
            # from the current state. Surface the message verbatim so
            # Claude can see which statuses ARE available.
            return SkillResult(ok=False, error=str(exc))
        except Exception as exc:  # noqa: BLE001
            return SkillResult(ok=False, error=f"jira_api_error: {exc}")

        return SkillResult(
            ok=True,
            data={
                "ticket_id": ticket_id,
                "new_status": applied["applied"],
                "transition_id": applied["transition_id"],
            },
        )
