"""Answer free-form questions over retrieved playbooks.

The Chat tab calls this: it retrieves the top-k playbooks for the user's
question and asks Sonnet to synthesise an answer that cites each claim back
to the playbook it came from. Citations use the playbook ``id`` as a stable
key, e.g. ``[hr-parking-fail]`` after a sentence.

Both a non-streaming ``answer_question`` and a streaming ``stream_answer``
are provided so the UI can render chunks live via ``st.write_stream``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator, Sequence

import config
from core.retrieval import Playbook


_SYSTEM_PROMPT = """You are an internal assistant for customer support
agents at a parking company. The person asking you questions is a
SUPPORT AGENT, not an end customer. Always answer from the perspective
of what the AGENT should do.

The person reading your answer IS the support agent. They ARE the
support. Never tell them to contact support — that IS them. Every
sentence must be an instruction for what THEY should do: check logs,
ask the customer, escalate, refund.

This is the single most important rule. Read it twice:

    The "you" / "ti" in your answer ALWAYS refers to the support
    agent reading your reply. It NEVER refers to the customer who
    submitted the ticket.

The provided playbooks are often written in customer-facing voice
(e.g. "If you got a fine, contact support"). You MUST rewrite every
such instruction into agent-facing voice before emitting it. Do not
parrot the playbook's customer voice — translate it into actions the
agent takes.

REQUIRED phrasing (always use this style):
- "Ask the customer to provide a screenshot of the transaction"
- "Ask the customer for the license plate and timestamp"
- "Check the transaction logs in Graylog for that id"
- "Check Jira for related tickets on the same session"
- "Verify the parking session in the operator dashboard"
- "Refund via the payment-provider console"
- "Escalate to engineering with the session id and Graylog snippet"
- "Inform the customer that the second charge is an authorization
  hold and will release in 3–7 business days"
- Croatian equivalents: "Zatraži od korisnika...", "Provjeri logove
  u Graylogu...", "Eskaliraj na...", "Javi korisniku da..."

FORBIDDEN phrasing — these address the customer and must NEVER appear
in your output. Note: the most insidious of these is any variant of
"contact support", because YOUR READER IS support. Telling support to
contact support is nonsense.
- "Contact support" / "Reach out to support" / "Reach out to the
  support team" / "Report the issue" / "Report this to support" /
  "Get in touch with support"
- "Attach a screenshot" / "Send us a screenshot"
- "If you got a fine" / "If you notice the charge"
- "Please provide..." (when directed at the customer)
- Croatian equivalents to avoid: "Kontaktiraj podršku" /
  "Kontaktirajte podršku" / "Obratite se podršci" / "Javi se podršci"
  / "Prijavi problem" / "Prijavite problem" / "Priloži snimku" /
  "Priložite snimku" / "Ako si dobio/la kaznu" / "Ako primijetiš
  naplatu" — ALL of these talk to the customer.

When you need to reference what the customer should be told, frame
it as agent-driven: "Tell the customer that..." / "Reply to the
customer with..." / "Javi korisniku da..." — NOT as direct address
to the customer.

A correct answer looks like a step-by-step playbook for the agent:
  1. Evidence to gather from the customer (what to ask for).
  2. Internal systems to check (what fields, what logs, what dashboard).
  3. Diagnostic question (e.g. "is it an auth hold or a real charge?").
  4. Concrete action (refund / escalate / reply).
  5. The message the agent should send back to the customer, if any.

PII rule — non-negotiable:

NEVER repeat personal data from the agent's question in your answer.
That includes (but is not limited to):
- Names (first or last)
- Email addresses
- Phone numbers
- OIB / national ID / tax ID numbers
- IBAN / bank account numbers
- Credit / debit card numbers (full or partial)
- License plates / registration numbers
- Home or business addresses
- Customer-account ids that look like personal handles

Refer to the customer generically — "the customer" in English,
"korisnik" / "korisnica" / "kupac" in Croatian. If the question
includes "Korisnik Ivan Horvat, OIB 12345678901, email ivan@test.com,
traži povrat …", your answer must read "Korisnik traži povrat …" and
never mention Ivan, the OIB, or the email. The reason: your output
flows into operator UIs that are read, logged, and sometimes copy-
pasted into tickets — every echoed PII expands the data-protection
blast radius for no benefit.

When the agent needs to look up the customer in internal tools, say
"look the customer up by the license plate / email / OIB they
provided" — not by repeating the value.

Grounding rules:
- Reply in the same language as the question (Croatian → Croatian
  answer; English → English answer). The agent-facing rule applies in
  every language.
- Use ONLY facts present in the provided playbooks. Do not invent
  systems, fields, timelines, or actions the playbooks don't describe.
- Every factual claim must be followed by an inline citation in the
  form [playbook-id], using the exact ids in the Sources list.
  Combine ids as [id-a][id-b] when a sentence draws from several.
- If the playbooks don't contain enough information to answer, say so
  explicitly and tell the agent what to escalate or investigate next.

Output: plain markdown, no surrounding code fence. Be concise — 3–6
short paragraphs or a short bullet list of agent-facing actions.

Before you send your final answer, scan it for the FORBIDDEN phrases
above. If any sentence reads as if you're talking to the end customer,
rewrite it as an instruction to the agent."""


# Matches IDs like "hr-parking-fail" or "scs-westfield-open-session-daily-check__c72ee4".
_CITATION_RE = re.compile(r"\[([a-z0-9][a-z0-9_\-]+)\]")


@dataclass
class AnswerResult:
    answer: str
    cited_ids: list[str]


def _build_user_prompt(*, question: str, playbooks: Sequence[Playbook]) -> str:
    sources = [
        f"[{pb.id}] {pb.title}\n{pb.body.strip()}"
        for pb in playbooks
    ]
    return (
        f"Question:\n{question}\n\n"
        "Sources (use these exact ids in citations):\n\n"
        + "\n\n---\n\n".join(sources)
    )


def extract_cited_ids(text: str, playbooks: Sequence[Playbook]) -> list[str]:
    """Return cited playbook ids in order of first appearance, deduped.

    Only ids that are present in ``playbooks`` (the retrieved top-K) are
    returned — used for the ``cited_ids`` field which records "which of
    the retrieved sources did the model actually anchor on".
    """
    known = {pb.id for pb in playbooks}
    seen: list[str] = []
    for match in _CITATION_RE.finditer(text):
        cid = match.group(1)
        if cid in known and cid not in seen:
            seen.append(cid)
    return seen


def extract_all_cited_ids(text: str) -> list[str]:
    """Return every ``[id]`` token in the text in order of first appearance.

    Unlike :func:`extract_cited_ids`, this does NOT filter against the
    retrieved set — the caller resolves each id against the full corpus
    later to build the citation index. The point is that the model may
    legitimately cite a playbook that wasn't in the top-K (the LLM has
    "seen" them all through fine-tuning / context bleed), and the UI
    should still resolve every citation to a real playbook instead of
    rendering an unknown-source marker.
    """
    seen: list[str] = []
    for match in _CITATION_RE.finditer(text):
        cid = match.group(1)
        if cid not in seen:
            seen.append(cid)
    return seen


def _get_client(client):
    if client is not None:
        return client
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    from anthropic import Anthropic

    return Anthropic(api_key=config.ANTHROPIC_API_KEY)


def answer_question(
    *,
    question: str,
    playbooks: Sequence[Playbook],
    client=None,
) -> AnswerResult:
    """Blocking call: returns the full answer + extracted citations."""
    if not playbooks:
        return AnswerResult(answer="(No playbooks retrieved.)", cited_ids=[])
    client = _get_client(client)
    user_prompt = _build_user_prompt(question=question, playbooks=playbooks)
    response = client.messages.create(
        model=config.CHAT_MODEL,
        max_tokens=config.CHAT_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = "".join(getattr(b, "text", "") for b in response.content).strip()
    return AnswerResult(answer=text, cited_ids=extract_cited_ids(text, playbooks))


def stream_answer(
    *,
    question: str,
    playbooks: Sequence[Playbook],
    client=None,
) -> Iterator[str]:
    """Yield answer chunks as they arrive. Suitable for ``st.write_stream``."""
    if not playbooks:
        yield "(No playbooks retrieved.)"
        return
    client = _get_client(client)
    user_prompt = _build_user_prompt(question=question, playbooks=playbooks)
    with client.messages.stream(
        model=config.CHAT_MODEL,
        max_tokens=config.CHAT_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            yield chunk
