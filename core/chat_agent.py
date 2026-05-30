"""Agentic chat — Claude tool_use loop tuned for operator Q&A.

Differences vs. ``core.planner`` (which drives ticket triage):

* **Read-only skills only.** Filtered via ``chat_tools_for_playbook`` so
  the operator can never accidentally trigger a write from a research
  query. The Knowledge tab is for looking, not acting.
* **No HITL.** Operator IS the user; whatever Claude says lands directly
  in the chat bubble. No pending actions, no audit log row per call.
* **Token-level streaming.** Final-answer text is forwarded delta by
  delta as it arrives from Anthropic, so the chat bubble fills up
  word-by-word. Skill execution events fire inline between text
  segments, ordered as Claude emits them.
* **One playbook context.** Planner gets the matched playbook in full;
  chat agent also gets the top playbook's body so prose stays grounded
  in the same domain knowledge the operator sees in Knowledge view.

Callers pass an ``on_event`` callback. We invoke it for every
SSE-style milestone — the router wraps this into actual SSE frames.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable

import config
from core.retrieval import Playbook
from core.skills.registry import REGISTRY, chat_tools_for_playbook


_SYSTEM_PROMPT = """\
You are an expert support agent having a conversation with an operator.
The operator asks you questions about customer issues. You have access
to skills to look up real data in company systems. When the operator
mentions a plate number, transaction, or specific customer issue —
use your skills to look up the data BEFORE answering. Combine playbook
knowledge with real data from skills. Be conversational, not formal.
Answer in the same language as the operator.

Strict rules:

1. **Look up data when the operator names a specific thing.** Plate,
   session id, transaction reference, customer email — call the
   relevant skill before composing your answer. Reading is free.

2. **Don't fabricate data.** If a lookup returns no record, say so
   honestly. Never invent a transaction, an amount, or a session id.
   "I couldn't find anything matching that plate" is a fine answer.

3. **Generic how-to questions don't need skills.** "How do I close a
   stuck session?" / "What's the refund process?" — answer from the
   playbook knowledge directly, no lookups needed.

4. **Be concise.** This is a chat, not a Jira reply. 2-5 sentences is
   usually enough. Add a list only when the operator asked for one.

5. **Match the operator's language.** Croatian in, Croatian out. German
   in, German out. Mixed in — whichever language dominates.
"""


_MAX_ITERATIONS = 8


@dataclass
class ChatAgentResult:
    """Returned by ``run_agentic_chat`` so the daemon thread can persist
    the final state to the chat_sessions row."""
    answer: str
    iterations: int
    skills_called: list[str]


# Event types emitted via on_event:
#   ('skill_executing', {'skill': str, 'params': dict})  - tool_use complete, about to run
#   ('skill_executed',  {'skill': str, 'params': dict, 'ok': bool,
#                        'result': dict | None, 'error': str | None, 'elapsed_ms': int})
#   ('composing',       {})  - first text delta about to be forwarded
#   ('token',           {'text': str})  - one text delta from Claude


EventCallback = Callable[[str, dict[str, Any]], None]


def run_agentic_chat(
    *,
    question: str,
    playbook: Playbook,
    on_event: EventCallback,
    client: Any = None,
    extra_skills: list[str] | None = None,
) -> ChatAgentResult:
    """Run the agentic chat loop. Returns the final answer text plus stats.

    ``extra_skills`` augments the playbook's ``allowed_skills`` — used
    by the router when a plate-shaped token in the question triggers
    forced agentic mode regardless of which playbook matched. Without
    this, a generic ``how-to`` playbook would deny the agent the
    lookups it needs even when the operator clearly asked for a
    specific record check.

    Raises whatever the Anthropic SDK or a skill raises — the caller
    (daemon thread) catches and marks the session ``error``.
    """
    if client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        from anthropic import Anthropic

        client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    base_skills = playbook.metadata.get("allowed_skills") or []
    combined_skills = list(dict.fromkeys([*base_skills, *(extra_skills or [])]))
    tools = chat_tools_for_playbook(combined_skills)
    if not tools:
        raise ValueError(
            "no read-only skills available for this run — caller should "
            "fall back to plain answerer"
        )

    initial_user_prompt = _build_initial_prompt(question, playbook)
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": initial_user_prompt}
    ]
    final_answer = ""
    skills_called: list[str] = []
    composing_emitted = False

    import time as _time

    for iteration in range(1, _MAX_ITERATIONS + 1):
        # Drive one Claude turn with streaming so text deltas can be
        # forwarded to the operator AS they arrive. Tool_use blocks are
        # collected to completion in this iteration; we execute them
        # after the stream finishes, push results back, and loop.
        with client.messages.stream(
            model=config.CHAT_MODEL,
            max_tokens=config.CHAT_MAX_TOKENS,
            system=_SYSTEM_PROMPT,
            messages=messages,
            tools=tools,
        ) as stream:
            # Per-stream state: current text buffer (per text block) and
            # current tool_use being accumulated (one at a time — the
            # API guarantees blocks don't interleave on the wire).
            current_text_block: str = ""
            current_tool: dict[str, Any] | None = None
            text_buffers: list[str] = []
            tool_uses: list[dict[str, Any]] = []

            for event in stream:
                etype = event.type
                if etype == "content_block_start":
                    block = event.content_block
                    if block.type == "text":
                        current_text_block = ""
                    elif block.type == "tool_use":
                        current_tool = {
                            "id": block.id,
                            "name": block.name,
                            "input_buffer": "",
                        }
                elif etype == "content_block_delta":
                    delta = event.delta
                    dtype = getattr(delta, "type", None)
                    if dtype == "text_delta":
                        if not composing_emitted:
                            on_event("composing", {})
                            composing_emitted = True
                        on_event("token", {"text": delta.text})
                        current_text_block += delta.text
                    elif dtype == "input_json_delta":
                        if current_tool is not None:
                            current_tool["input_buffer"] += delta.partial_json
                elif etype == "content_block_stop":
                    if current_tool is not None:
                        # Parse buffered JSON into the actual params dict
                        try:
                            params = (
                                json.loads(current_tool["input_buffer"])
                                if current_tool["input_buffer"]
                                else {}
                            )
                        except json.JSONDecodeError:
                            params = {}
                        tool_uses.append(
                            {
                                "id": current_tool["id"],
                                "name": current_tool["name"],
                                "input": params,
                            }
                        )
                        current_tool = None
                    elif current_text_block:
                        text_buffers.append(current_text_block)
                        current_text_block = ""
                # Other event types (message_start, message_delta,
                # message_stop) carry no inline payload we need to forward.

            final_msg = stream.get_final_message()

        # Append assistant message to history (using the canonical
        # content blocks from the SDK so the next iteration's tool_use
        # references resolve cleanly).
        messages.append(
            {"role": "assistant", "content": final_msg.content}
        )

        # If Claude didn't ask for any tool calls, we're done.
        if not tool_uses:
            final_answer = "".join(text_buffers)
            return ChatAgentResult(
                answer=final_answer,
                iterations=iteration,
                skills_called=skills_called,
            )

        # Execute each tool_use, build tool_result blocks for next turn.
        tool_results: list[dict[str, Any]] = []
        for tu in tool_uses:
            name = tu["name"]
            params = tu["input"]
            call_id = tu["id"]  # Anthropic-issued unique id per tool_use
            skills_called.append(name)
            # ``call_id`` is the join key the frontend uses to fold the
            # 'executing' row into the 'executed' row. Params-based
            # matching is fragile (type coercion across JSON round trips
            # can break equality) so we always emit the canonical id.
            on_event(
                "skill_executing",
                {"skill": name, "params": params, "call_id": call_id},
            )
            started = _time.time()
            ok = False
            result_data: dict[str, Any] | None = None
            err: str | None = None
            try:
                skill_cls = REGISTRY.get(name)
                if skill_cls is None:
                    err = f"unknown skill: {name}"
                else:
                    skill = skill_cls()
                    res = skill.execute(**params)
                    ok = bool(res.ok)
                    result_data = res.data if res.ok else None
                    err = res.error
            except Exception as exc:  # noqa: BLE001
                err = f"{type(exc).__name__}: {exc}"
            elapsed_ms = int((_time.time() - started) * 1000)
            on_event(
                "skill_executed",
                {
                    "skill": name,
                    "params": params,
                    "call_id": call_id,
                    "ok": ok,
                    "result": result_data,
                    "error": err,
                    "elapsed_ms": elapsed_ms,
                },
            )
            # Anthropic accepts string content for tool_result. We
            # serialize the data (or error) compactly — Claude reads
            # this verbatim, so keep it real JSON not a description.
            if ok and result_data is not None:
                payload = json.dumps(result_data, ensure_ascii=False)
            else:
                payload = json.dumps({"error": err or "unknown_error"})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": payload,
                }
            )

        messages.append({"role": "user", "content": tool_results})

    # Iteration cap reached — return whatever text we accumulated last.
    return ChatAgentResult(
        answer=final_answer or "(Agent reached the iteration cap without producing a final answer.)",
        iterations=_MAX_ITERATIONS,
        skills_called=skills_called,
    )


def _build_initial_prompt(question: str, playbook: Playbook) -> str:
    parts = [
        "# Operator question",
        question,
        "",
        "# Matched playbook (for domain context)",
        f"Title: {playbook.title}",
        f"ID: {playbook.id}",
        "",
        playbook.body,
    ]
    return "\n".join(parts)
