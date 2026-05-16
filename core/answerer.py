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


_SYSTEM_PROMPT = """You answer questions using a small set of provided
playbooks. You may use ONLY the facts present in those playbooks.

Rules:
- Reply in the same language as the question.
- Every factual claim must be followed by an inline citation in the form
  [playbook-id], using the exact ids given in the Sources list below.
  Combine multiple ids as [id-a][id-b] when a sentence draws from several.
- If the playbooks do not contain enough information to answer, say so
  explicitly — do not invent facts, timelines, or actions.
- Output plain markdown. Do NOT wrap the whole answer in a code fence.
- Be concise: 3–6 short paragraphs or a short bullet list."""


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
    """Return cited playbook ids in order of first appearance, deduped."""
    known = {pb.id for pb in playbooks}
    seen: list[str] = []
    for match in _CITATION_RE.finditer(text):
        cid = match.group(1)
        if cid in known and cid not in seen:
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
        model=config.DRAFTER_MODEL,
        max_tokens=config.DRAFTER_MAX_TOKENS,
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
        model=config.DRAFTER_MODEL,
        max_tokens=config.DRAFTER_MAX_TOKENS,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            yield chunk
