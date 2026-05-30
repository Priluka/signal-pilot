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
- Trust the matched playbook. It was selected by retrieval as the best
  match for this ticket — base your draft on its diagnosis and steps.
  Do NOT override the playbook with your own interpretation of the
  ticket (e.g. "this isn't really about X, it's about Y"). If the
  playbook says the ghost charge happens because the rental car is
  still linked to the customer's account, that is the diagnosis you
  use; don't tell the customer "we don't handle car rentals".
- Stay strictly inside the playbook's "Typical resolution flow" and
  "Typical actions" — do not invent capabilities, timelines, or refunds
  the playbook does not authorize.
- Honor every constraint in the playbook's "Safety constraints" section
  if present. If a constraint forbids autonomous action, recommend
  "escalate_to_human".
- Never promise to contact a vendor or third party unless the playbook
  lists that as a typical action.
- If the playbook indicates this case needs human verification, set
  recommended_action to "send_with_review" or "escalate_to_human".

Tone rules:
- When the ticket describes an URGENT situation — a fine being issued
  right now, a barrier blocking entry/exit, payment failing at the gate,
  or any other "I'm stuck and the meter is running" scenario — open
  with empathy and immediate-help framing. Never open such a reply
  with a channel disclaimer ("this channel is for B2B partners…"),
  legal boilerplate, or a "thank you for contacting us" form letter.
  The first sentence must acknowledge the urgency and signal action.
- For non-urgent tickets, a warmer professional opener is fine, but
  still keep it short — never lead with disclaimers.

Diagnosis rules:
- Always include at least one concrete diagnosis or likely explanation
  drawn from the playbook, even when you also need to ask the customer
  for more information. Never send a reply whose entire body is "could
  you tell us more about X, Y, Z?" with zero diagnostic content. Lead
  with what the playbook says is most likely happening, then (if
  needed) ask for the specific evidence required to confirm.
- The shape is: "[acknowledgement / urgency] + [likely cause from
  playbook] + [concrete next step or info needed]". All three parts.

Missing-attachment rule:
- The user prompt includes an `attachments` flag. When the customer's
  message references an attachment ("see attached", "vidi prilog",
  "im Anhang", "allegato", "screenshot u prilogu", "trovate la foto",
  etc.) AND `attachments=false`, you MUST acknowledge the gap in
  your draft: e.g. "We did not receive an attachment with your ticket
  — could you please re-send the screenshot/photo?" / "Snimak nije
  stigao uz Vašu poruku — možete li ga ponovo poslati?" / "Ihr Anhang
  ist nicht bei uns angekommen — bitte schicken Sie das Bild erneut."
  Do NOT proceed as if you have seen the attachment. Do NOT write
  "based on the attached screenshot…" or "iz priložene snimke
  vidimo…" when no file actually arrived. The diagnosis must still
  come from the textual description, and the request for the
  attachment is in addition to (not instead of) the diagnosis.
- When `attachments=true`, you may reference the attached file
  naturally ("based on the screenshot you sent…") but only at the
  level of detail the customer's text already establishes — never
  invent specifics you would have had to see in the image.
- When `attachments=unknown`, do not claim visibility either way.

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
    raw = match.group(0)
    # ``strict=False`` lets json.loads accept literal newlines and tabs
    # inside string values — Sonnet/Opus occasionally emit a raw newline
    # in the draft body rather than the escaped ``\n``, which would
    # otherwise blow up parsing.
    return json.loads(raw, strict=False)


def _build_user_prompt(
    *,
    ticket_summary: str,
    ticket_description: str,
    playbook: Playbook,
    has_attachments: bool | None,
) -> str:
    if has_attachments is True:
        attach_line = "attachments: true (the customer sent file(s) with the ticket)"
    elif has_attachments is False:
        attach_line = (
            "attachments: false (no file is attached — even if the customer "
            "says they sent one, none arrived)"
        )
    else:
        attach_line = "attachments: unknown"
    return (
        "<ticket>\n"
        f"Summary: {ticket_summary}\n\n"
        f"Description:\n{ticket_description}\n\n"
        f"{attach_line}\n"
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
    has_attachments: bool | None = None,
    client=None,
) -> DraftResult:
    """Draft a reply for one ticket + one playbook.

    ``has_attachments`` flags whether the ticket actually carries
    files (vs. the customer merely claiming they sent one). When
    ``False``, the system prompt forces the draft to acknowledge the
    missing attachment instead of pretending to have seen it. When
    ``None`` we say "unknown" and the model is told not to claim
    visibility either way. ``client`` is injectable for tests.

    Retries up to three times when the model emits malformed JSON —
    Opus occasionally drops an unescaped quote inside the draft body
    that even ``strict=False`` can't recover. A fresh call with the
    same prompt usually yields valid output because of token-sampling
    variance.
    """
    if client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        from anthropic import Anthropic

        client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    user_prompt = _build_user_prompt(
        ticket_summary=ticket_summary,
        ticket_description=ticket_description,
        playbook=playbook,
        has_attachments=has_attachments,
    )

    raw_text: str = ""
    payload: dict | None = None
    last_parse_error: Exception | None = None
    for _attempt in range(3):
        response = client.messages.create(
            model=config.DRAFTER_MODEL,
            max_tokens=config.DRAFTER_MAX_TOKENS,
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw_text = "".join(
            getattr(block, "text", "") for block in response.content
        ).strip()
        try:
            payload = _extract_json(raw_text)
            break
        except (json.JSONDecodeError, ValueError) as exc:
            last_parse_error = exc
            # No backoff — the issue is sampling variance, not server load.
            # Just call again immediately.
            continue
    if payload is None:
        raise ValueError(
            f"Drafter returned malformed JSON after 3 attempts: {last_parse_error}"
        )
    action = payload.get("recommended_action")
    if action not in _VALID_ACTIONS:
        raise ValueError(f"Drafter returned unknown action {action!r}")
    return DraftResult(
        draft=str(payload.get("draft", "")).strip(),
        recommended_action=action,
        rationale=str(payload.get("rationale", "")),
        raw_response=raw_text,
    )
