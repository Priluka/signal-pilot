"""Skill: ``bmove_user_lookup``.

Looks up an end-user in the Bmove backend by plate or email. The agent
uses this to confirm the customer is registered, see what vehicles are
on file, whether Ticketless is enabled, the saved payment method and
its current card status, and whether they carry any outstanding debt
before drafting a reply.

Read-only, auto-execute.
"""
from __future__ import annotations

from typing import Any

from core.skills.base import Skill, SkillResult
from core.skills.external import mock_data
from core.skills.registry import register


@register
class BmoveUserLookup(Skill):
    name = "bmove_user_lookup"

    description = (
        "Look up a Bmove end-user by plate or email. Returns user_id, "
        "masked email, registered flag, vehicles (each with plate + "
        "ticketless_enabled), active_sessions, outstanding_debts, "
        "payment_method (last 4 digits), card_status (ACTIVE / EXPIRED / "
        "BLOCKED), last_activity. Returns null when the plate/email "
        "isn't on file (use null as the signal — do not invent users)."
    )

    is_write = False

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Vehicle registration plate.",
            },
            "email": {
                "type": "string",
                "description": "Customer email — supports the masked form (e.g. 'k***@gmail.com').",
            },
        },
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        plate = params.get("plate")
        email = params.get("email")
        if not plate and not email:
            return SkillResult(ok=False, error="provide plate or email")
        row = mock_data.lookup_bmove(plate=plate, email=email)
        return SkillResult(
            ok=True,
            data={
                "queried_by": "plate" if plate else "email",
                "found": row is not None,
                "user": row,
            },
        )
