"""Skill: ``parkis_lookup``.

Looks up an on-street parking transaction in the ParkIS system (SMS /
app payments to local Croatian / regional parking authorities). The
agent uses this to verify whether a Croatian end-user's claimed
payment actually reached the operator's system.

Read-only, auto-execute.
"""
from __future__ import annotations

from typing import Any

from core.skills.base import Skill, SkillResult
from core.skills.external import mock_data
from core.skills.registry import register


@register
class ParkisLookup(Skill):
    name = "parkis_lookup"

    description = (
        "Look up an on-street parking transaction in ParkIS for a "
        "specific plate. Returns transaction_id, plate, zone, "
        "start/end_time, amount, payment_method (SMS / APP), "
        "operator_confirmation, status (ACTIVE / EXPIRED / CANCELLED), "
        "sms_gateway. Returns null when no transaction exists for "
        "that plate (so the agent knows there is no data, rather than "
        "fabricating one)."
    )

    is_write = False

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Vehicle registration plate (e.g. 'ZG-1234-AB').",
            },
            "zone": {
                "type": "string",
                "description": "Optional zone filter, e.g. 'Zagreb Zone 2'.",
            },
            "date": {
                "type": "string",
                "description": "Optional date filter (YYYY-MM-DD).",
            },
        },
        "required": ["plate"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        plate = str(params.get("plate") or "").strip()
        if not plate:
            return SkillResult(ok=False, error="empty_plate")
        row = mock_data.lookup_parkis(
            plate=plate,
            zone=params.get("zone"),
            date=params.get("date"),
        )
        return SkillResult(
            ok=True,
            data={
                "plate": plate,
                "found": row is not None,
                "transaction": row,
            },
        )
