"""Pre-classifier: gate the retrieval pipeline.

One Claude call decides whether a ticket is a real support request, an
internal-only log, or spam. Only ``support_request`` should ever reach the
retrieval+drafter path; the other two are routed to auto-close.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

import config


TicketClassification = Literal["support_request", "internal_log", "spam_or_junk"]

_VALID_LABELS: tuple[TicketClassification, ...] = (
    "support_request",
    "internal_log",
    "spam_or_junk",
)

_SYSTEM_PROMPT = """You are a triage classifier for an inbound support queue.

For each ticket, return JSON with this exact schema:
{
  "label": "support_request" | "internal_log" | "spam_or_junk",
  "confidence": <float 0..1>,
  "reason": "<one short sentence>"
}

Definitions:
- "support_request": a real user or partner asking for help, reporting a bug,
  or chasing a refund/invoice/fine — anything that needs a reply.
- "internal_log": automated reports, monitoring alerts, internal status
  threads, meeting notes, or anything the team writes to itself. No external
  reply required.
- "spam_or_junk": marketing/cold-outreach, phishing, quarantine notifications
  from M365, or otherwise non-actionable.

Respond with ONLY the JSON object. No prose, no markdown fence."""

_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class ClassificationResult:
    label: TicketClassification
    confidence: float
    reason: str
    raw_response: str


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of the model response.

    Models occasionally wrap JSON in a ```json fence or add a stray sentence;
    we extract the outer object and parse that.
    """
    match = _JSON_OBJECT_RE.search(text)
    if not match:
        raise ValueError(f"Classifier returned no JSON object: {text!r}")
    return json.loads(match.group(0))


def _build_user_prompt(*, summary: str, description: str, reporter_email: str | None, labels: list[str]) -> str:
    return (
        f"Summary: {summary}\n"
        f"Reporter: {reporter_email or 'unknown'}\n"
        f"Labels: {', '.join(labels) if labels else '(none)'}\n\n"
        f"Description:\n{description}"
    )


def classify_ticket(
    *,
    summary: str,
    description: str,
    reporter_email: str | None = None,
    labels: list[str] | None = None,
    client=None,
) -> ClassificationResult:
    """Classify one ticket. Pass ``client`` to inject a mocked Anthropic client in tests."""
    if client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        from anthropic import Anthropic

        client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    user_prompt = _build_user_prompt(
        summary=summary,
        description=description,
        reporter_email=reporter_email,
        labels=labels or [],
    )

    response = client.messages.create(
        model=config.CLASSIFIER_MODEL,
        max_tokens=config.CLASSIFIER_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Anthropic SDK returns content blocks; we expect a single text block.
    raw_text = "".join(getattr(block, "text", "") for block in response.content).strip()
    payload = _extract_json(raw_text)
    label = payload.get("label")
    if label not in _VALID_LABELS:
        raise ValueError(f"Classifier returned unknown label {label!r}")
    return ClassificationResult(
        label=label,
        confidence=float(payload.get("confidence", 0.0)),
        reason=str(payload.get("reason", "")),
        raw_response=raw_text,
    )
