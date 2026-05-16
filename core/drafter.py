"""Drafter: produces a customer-ready reply for a ticket given a matched playbook."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

import config
from core.retrieval import Playbook


RecommendedAction = Literal[
    "send_draft",
    "send_with_review",
    "escalate_to_human",
    "auto_close",
]

_VALID_ACTIONS: tuple[RecommendedAction, ...] = (
    "send_draft",
    "send_with_review",
    "escalate_to_human",
    "auto_close",
)

_SYSTEM_PROMPT = """You are a support-reply drafter. You receive one customer
ticket plus a matching playbook. You produce a reply the customer would
actually receive.

Hard rules:
- Reply in the same language as the customer's message.
- Stay strictly inside the playbook's "Typical resolution flow" and "Typical
  actions" — do not invent capabilities, timelines, or refunds the playbook
  does not authorize.
- Honor every constraint in the playbook's "Safety constraints" section if
  present. If a constraint forbids autonomous action, recommend
  "escalate_to_human".
- Never promise to contact a vendor or third party unless the playbook lists
  that as a typical action.
- If the playbook indicates this case needs human verification, set
  recommended_action to "send_with_review" or "escalate_to_human".

Output exactly this JSON object (no prose, no markdown fence):
{
  "draft": "<the reply text the customer would read>",
  "recommended_action": "send_draft" | "send_with_review" | "escalate_to_human" | "auto_close",
  "rationale": "<one short sentence explaining the action choice>"
}"""

_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class DraftResult:
    draft: str
    recommended_action: RecommendedAction
    rationale: str
    raw_response: str


def _extract_json(text: str) -> dict:
    match = _JSON_OBJECT_RE.search(text)
    if not match:
        raise ValueError(f"Drafter returned no JSON object: {text!r}")
    return json.loads(match.group(0))


def _build_user_prompt(*, ticket_summary: str, ticket_description: str, playbook: Playbook) -> str:
    return (
        "<ticket>\n"
        f"Summary: {ticket_summary}\n\n"
        f"Description:\n{ticket_description}\n"
        "</ticket>\n\n"
        "<playbook>\n"
        f"Title: {playbook.title}\n"
        f"ID: {playbook.id}\n"
        f"Resolution pattern: {playbook.resolution_pattern}\n\n"
        f"{playbook.body.strip()}\n"
        "</playbook>"
    )


def draft_reply(
    *,
    ticket_summary: str,
    ticket_description: str,
    playbook: Playbook,
    client=None,
) -> DraftResult:
    """Draft a reply for one ticket + one playbook. ``client`` is injectable for tests."""
    if client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        from anthropic import Anthropic

        client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    user_prompt = _build_user_prompt(
        ticket_summary=ticket_summary,
        ticket_description=ticket_description,
        playbook=playbook,
    )

    response = client.messages.create(
        model=config.DRAFTER_MODEL,
        max_tokens=config.DRAFTER_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw_text = "".join(getattr(block, "text", "") for block in response.content).strip()
    payload = _extract_json(raw_text)
    action = payload.get("recommended_action")
    if action not in _VALID_ACTIONS:
        raise ValueError(f"Drafter returned unknown action {action!r}")
    return DraftResult(
        draft=str(payload.get("draft", "")).strip(),
        recommended_action=action,
        rationale=str(payload.get("rationale", "")),
        raw_response=raw_text,
    )
