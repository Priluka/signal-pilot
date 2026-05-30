"""Skill: ``datatrans_transaction``.

Looks up a single transaction in the Datatrans payment processor by
session id or transaction id. The agent uses this as the source of
truth for whether a card was charged, when it settled, and whether the
charge is refundable.

Read-only, auto-execute.
"""
from __future__ import annotations

from typing import Any

from core.skills.base import Skill, SkillResult
from core.skills.external import mock_data
from core.skills.registry import register


@register
class DatatransTransaction(Skill):
    name = "datatrans_transaction"

    description = (
        "Look up a single Datatrans transaction by session reference or "
        "transaction id. Returns transaction_id, amount (cents), "
        "currency, status (settled / authorized / failed / refunded), "
        "card_type, last4, 3ds_status, settled_at, refundable, and "
        "error_message (when failed). Use this to confirm the customer "
        "actually got charged before promising a refund or denying one."
    )

    is_write = False

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "reference": {
                "type": "string",
                "description": (
                    "Session id (e.g. 'sess-88421') or full transaction "
                    "id (e.g. 'DT-20260527-882341'). Either works — the "
                    "skill looks both up."
                ),
            },
        },
        "required": ["reference"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        reference = str(params.get("reference") or "").strip()
        if not reference:
            return SkillResult(ok=False, error="empty_reference")
        row = mock_data.lookup_datatrans(reference=reference)
        return SkillResult(
            ok=True,
            data={
                "reference": reference,
                "found": row is not None,
                "transaction": row,
            },
        )
