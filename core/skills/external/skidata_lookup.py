"""Skill: ``skidata_session_lookup``.

Looks up a parking-garage session in SKIDATA (LPR barriers, used in
Vienna garages among others). The agent uses this to verify the
classic "stuck session" pattern — entry recognised, exit missed,
barrier opened manually by garage staff — before drafting any
customer reply about an open session or unpaid debt.

Read-only, auto-execute.
"""
from __future__ import annotations

from typing import Any

from core.skills.base import Skill, SkillResult
from core.skills.external import mock_data
from core.skills.registry import register


@register
class SkidataSessionLookup(Skill):
    name = "skidata_session_lookup"

    description = (
        "Look up the most recent SKIDATA garage session for a plate. "
        "Returns session_id, plate, garage, entry/exit times, status "
        "(OPEN / CLOSED / DEBT), lpr_entry, lpr_exit, barrier_override "
        "(NONE / MANUAL_STAFF / HOTLINE / EMERGENCY), tariff_zone, and "
        "amount_due. Use this to verify stuck-session claims before "
        "telling the customer anything about their visit."
    )

    is_write = False

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "plate": {
                "type": "string",
                "description": "Vehicle registration plate (e.g. 'W-38702T').",
            },
            "garage": {
                "type": "string",
                "description": (
                    "Optional garage name filter (e.g. 'Schwarzenbergplatz'). "
                    "Matches loosely against the stored garage."
                ),
            },
        },
        "required": ["plate"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        plate = str(params.get("plate") or "").strip()
        if not plate:
            return SkillResult(ok=False, error="empty_plate")
        row = mock_data.lookup_skidata(plate=plate, garage=params.get("garage"))
        return SkillResult(
            ok=True,
            data={
                "plate": plate,
                "found": row is not None,
                "session": row,
            },
        )
