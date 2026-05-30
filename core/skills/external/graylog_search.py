"""Skill: ``graylog_search``.

Free-text search across Graylog's structured logs. The agent uses this
to verify what really happened on a transaction — was the card
charged, did the SMS arrive, did the LPR camera misfire — before it
tells the customer anything.

Read-only, auto-execute. No HITL approval required (no side effects).

Mock implementation today; swap ``mock_data.search_graylog`` for an
HTTP POST to ``/api/search/messages`` once Ivan ships credentials.
"""
from __future__ import annotations

from typing import Any

from core.skills.base import Skill, SkillResult
from core.skills.external import mock_data
from core.skills.registry import register


@register
class GraylogSearch(Skill):
    name = "graylog_search"

    description = (
        "Search Graylog logs for payment / session / LPR events. Supports "
        "filters like 'plate:W-55123K' and 'status:SETTLED' joined with "
        "AND. Returns matching log rows newest-last, each with timestamp, "
        "plate, amount, status, gateway, session_id, and error_code. Use "
        "this to verify what the systems actually recorded before "
        "confirming anything to the customer."
    )

    is_write = False

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Graylog query string. Supports 'plate:VAL', 'status:VAL', "
                    "'gateway:VAL'. Example: 'plate:W-55123K AND status:SETTLED'."
                ),
            },
            "timerange": {
                "type": "string",
                "description": (
                    "Human-readable window like 'last 24 hours' or "
                    "'last 7 days'. Currently advisory — the mock ignores "
                    "the window. Real backend will respect it."
                ),
                "default": "last 7 days",
            },
            "limit": {
                "type": "integer",
                "description": "Max rows to return.",
                "default": 25,
                "minimum": 1,
                "maximum": 200,
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        query = str(params.get("query") or "").strip()
        if not query:
            return SkillResult(ok=False, error="empty_query")
        limit = int(params.get("limit") or 25)
        messages = mock_data.search_graylog(query=query, limit=limit)
        return SkillResult(
            ok=True,
            data={
                "query": query,
                "timerange": params.get("timerange") or "last 7 days",
                "total_results": len(messages),
                "messages": messages,
            },
        )
