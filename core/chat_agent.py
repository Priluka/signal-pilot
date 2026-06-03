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
import logging
import random
import re
import threading
import time as _time_mod
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass
from typing import Any, Callable

log = logging.getLogger(__name__)

import config
from core import chat_threads
from core.metrics import (
    CHAT_ANTHROPIC_RETRIES,
    CHAT_COMPACTION_HITS,
    CHAT_COST_CAP_HITS,
    CHAT_SKILL_DURATION,
    CHAT_TURN_COST,
    CHAT_TURN_DURATION,
    CHAT_TURNS_TOTAL,
)
from core.retrieval import Playbook
from core.skills.registry import REGISTRY, chat_tools_for_playbook
from core.tracing import get_tracer

_tracer = get_tracer("signal-pilot.chat_agent")


# ---------------------------------------------------------------------------
# Skill execution hardening.
# ---------------------------------------------------------------------------
#
# Production skills (Bmove, Datatrans, SKIDATA, Graylog) hit external
# HTTP services with their own latency / failure shapes. A hung skill
# would lock the agent loop indefinitely. We run every skill in a
# bounded thread pool with a per-call timeout — when it fires, the
# underlying thread keeps running (Python can't cancel arbitrary
# threads) but the agent gives up waiting and feeds a timeout error
# back to Claude, who can reason about it.
#
# ``_SKILL_TIMEOUT_S`` is intentionally generous (30s) — most real
# skills resolve in <2s, and a 30s ceiling beats letting a single
# hanging request poison the whole turn.

_SKILL_TIMEOUT_S = 30.0
_SKILL_POOL_WORKERS = 8

# Sonnet 4.6 list pricing per Anthropic public docs. Updates here when
# the model changes — kept local so the cost surface uses one source
# of truth rather than scattered constants. Prices are USD per token
# (not per million) for arithmetic convenience.
_PRICE_INPUT_PER_TOKEN = 3.0 / 1_000_000
_PRICE_OUTPUT_PER_TOKEN = 15.0 / 1_000_000


def _estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens * _PRICE_INPUT_PER_TOKEN
        + output_tokens * _PRICE_OUTPUT_PER_TOKEN
    )


# ---------------------------------------------------------------------------
# Anthropic retry wrapper — Phase 10.
# ---------------------------------------------------------------------------
#
# The SDK's own retries don't cover every transient surface, especially
# during burst traffic on a shared account. We wrap each call we make
# (messages.stream, messages.create) in an exponential-backoff loop
# that retries on RateLimitError, OverloadedError (529), and any
# APIConnectionError. The retry budget is bounded (defaults to 4
# attempts with backoff 1s → 2s → 4s → 8s + jitter) so a sustained
# outage still bubbles up as a clean error to the operator instead of
# hanging forever.


def _is_retryable_anthropic(exc: BaseException) -> bool:
    """Whether the exception is a transient Anthropic-side failure we
    should retry. We import the SDK exception classes lazily so this
    module stays importable when the SDK isn't installed (e.g. in
    tests that monkey-patch the client). Also tolerates SDK version
    drift — newer versions add ``OverloadedError`` etc., which we
    handle generically via APIStatusError status_code."""
    try:
        from anthropic import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            InternalServerError,
            RateLimitError,
        )
    except ImportError:
        return False
    if isinstance(
        exc,
        (
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            InternalServerError,
        ),
    ):
        return True
    # 529 Overloaded is sometimes returned without a dedicated class.
    if isinstance(exc, APIStatusError):
        status = getattr(exc, "status_code", None)
        if status in (429, 502, 503, 504, 529):
            return True
    return False


def _with_anthropic_retries(callable_factory: Callable[[], Any]) -> Any:
    """Invoke a no-arg factory that performs the Anthropic call, with
    exponential backoff + jitter on retryable errors. ``callable_factory``
    is invoked fresh per attempt so any context-manager / streaming
    state gets a clean retry. Returns whatever the factory returns on
    success; re-raises the last exception when retries are exhausted.
    """
    max_attempts = max(1, config.ANTHROPIC_MAX_RETRIES + 1)
    backoff = config.ANTHROPIC_INITIAL_BACKOFF_S
    last_exc: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return callable_factory()
        except BaseException as exc:  # noqa: BLE001
            if not _is_retryable_anthropic(exc) or attempt >= max_attempts:
                raise
            last_exc = exc
            # Jitter prevents thundering-herd when multiple turns hit
            # the same rate limit simultaneously.
            sleep_for = backoff * (2 ** (attempt - 1))
            sleep_for += random.uniform(0, sleep_for * 0.25)
            log.warning(
                "anthropic retry attempt %d/%d after %s: %s",
                attempt,
                max_attempts,
                type(exc).__name__,
                exc,
            )
            CHAT_ANTHROPIC_RETRIES.labels(exception=type(exc).__name__).inc()
            _time_mod.sleep(sleep_for)
    # Defensive — loop above always returns or raises.
    if last_exc is not None:
        raise last_exc
    raise RuntimeError("unreachable: anthropic retry loop exited cleanly")

_skill_executor = ThreadPoolExecutor(
    max_workers=_SKILL_POOL_WORKERS, thread_name_prefix="chat-skill-"
)


def _safe_dumps(payload: Any) -> str:
    """``json.dumps`` with a ``default=str`` fallback. Production
    skill responses may contain datetimes, Decimals, UUIDs, or other
    non-JSON-native types — without this safeguard, a single such
    field crashes the whole agent loop. ``default=str`` coerces the
    offending value to its repr so the LLM still sees usable text."""
    try:
        return json.dumps(payload, ensure_ascii=False)
    except (TypeError, ValueError):
        return json.dumps(payload, ensure_ascii=False, default=str)


def _run_skill_with_timeout(skill_name: str, params: dict[str, Any]) -> tuple[
    bool, dict[str, Any] | None, str | None
]:
    """Resolve + execute a registered skill with a 30s ceiling. Returns
    ``(ok, data, err)``. Synchronous helper used by single-skill paths
    (planner loop). For the chat agent we use the split
    submit/await helpers below to run multiple skills concurrently
    within one assistant turn."""
    future, err = _submit_skill(skill_name, params)
    if future is None:
        return False, None, err
    return _await_skill(future, skill_name)


def _submit_skill(
    skill_name: str, params: dict[str, Any]
) -> tuple[Any | None, str | None]:
    """Phase 9A — start a skill on the pool without waiting. Returns
    ``(future, None)`` on success or ``(None, err_message)`` when the
    skill can't even be dispatched (unknown name, init failure). The
    caller pairs this with ``_await_skill`` later so multiple skills
    can run concurrently and the awaits happen in a determinate
    order."""
    skill_cls = REGISTRY.get(skill_name)
    if skill_cls is None:
        return None, f"unknown skill: {skill_name}"
    try:
        skill = skill_cls()
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"
    try:
        # Bind defaults so the closure captures the values at submit
        # time rather than reading them from the loop scope.
        future = _skill_executor.submit(
            lambda _s=skill, _p=params: _s.execute(**_p)
        )
    except Exception as exc:  # noqa: BLE001
        return None, f"submit failed: {type(exc).__name__}: {exc}"
    return future, None


def _await_skill(
    future: Any, skill_name: str
) -> tuple[bool, dict[str, Any] | None, str | None]:
    """Block on a previously-submitted skill future with the standard
    timeout. Mirror of the unified return shape used everywhere
    skill_executed events are emitted. Also runs Phase 12.7 response
    schema validation on success: if the skill declares an
    ``output_schema`` and the response doesn't match, downgrade to
    a clean schema-violation error rather than passing garbage to
    the LLM."""
    try:
        res = future.result(timeout=_SKILL_TIMEOUT_S)
    except FuturesTimeout:
        return (
            False,
            None,
            f"skill {skill_name} timed out after {_SKILL_TIMEOUT_S}s",
        )
    except Exception as exc:  # noqa: BLE001
        return False, None, f"{type(exc).__name__}: {exc}"
    ok = bool(res.ok)
    data = res.data if ok else None
    if ok and data is not None:
        validation_err = _validate_skill_output(skill_name, data)
        if validation_err is not None:
            return False, None, validation_err
    return ok, data, res.error


def _validate_skill_output(
    skill_name: str, data: dict[str, Any]
) -> str | None:
    """Return ``None`` if the skill's data matches its declared output
    schema (or the skill didn't declare one); otherwise return a clean
    one-line error string that the agent loop can surface as a skill
    failure. Uses ``jsonschema`` for validation when available."""
    skill_cls = REGISTRY.get(skill_name)
    if skill_cls is None:
        return None
    schema = getattr(skill_cls, "output_schema", None)
    if not schema:
        return None
    try:
        import jsonschema
    except ImportError:
        return None  # validation library unavailable — best-effort skip
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as exc:
        # Truncate the SDK's long path/message so the LLM gets a
        # one-liner it can reason about, not a multi-page stack.
        path = "/".join(str(p) for p in exc.absolute_path) or "<root>"
        return (
            f"skill {skill_name} response failed schema at "
            f"'{path}': {exc.message}"
        )
    except Exception as exc:  # noqa: BLE001
        return f"skill {skill_name} schema check error: {exc}"
    return None


# ---------------------------------------------------------------------------
# Interrupt registry — cooperative cancellation for in-flight turns.
# ---------------------------------------------------------------------------
#
# Claude Code's ESC pattern: the operator can stop the agent mid-loop.
# We can't kill a running Anthropic stream from outside, but we CAN
# check a flag at iteration boundaries and exit cleanly — so an
# interrupt fires at the next loop iteration (worst case ~5-10 seconds
# of trailing work). The daemon persists ``status='error'`` with a
# specific ``error_message`` so the UI can distinguish stop from real
# failure.


_interrupt_lock = threading.Lock()
_interrupt_set: set[int] = set()


def request_interrupt(turn_id: int) -> None:
    """Mark a turn for cancellation. The loop checks this flag at the
    top of each iteration; once observed the turn ends with a synthetic
    error_message and status='error'. Idempotent — safe to call twice.
    Public so the HTTP router can call it from its interrupt endpoint."""
    with _interrupt_lock:
        _interrupt_set.add(turn_id)


def _consume_interrupt(turn_id: int) -> bool:
    """Test-and-clear in one critical section so the flag never leaks
    onto a future turn that happens to reuse the same id (shouldn't —
    SQLite autoincrement is monotonic — but defence in depth)."""
    with _interrupt_lock:
        if turn_id in _interrupt_set:
            _interrupt_set.discard(turn_id)
            return True
        return False


# Marker string we persist on cancelled turns. Frontend keys on this
# exact prefix to render "Stopped by operator" instead of "Error".
INTERRUPT_ERROR_PREFIX = "Cancelled by operator"
COST_CAP_ERROR_PREFIX = "Per-turn cost cap exceeded"


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
            ok, result_data, err = _run_skill_with_timeout(name, params)
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
                payload = _safe_dumps(result_data)
            else:
                payload = _safe_dumps({"error": err or "unknown_error"})
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


def _block_to_dict(block: Any) -> dict[str, Any]:
    """Convert an Anthropic SDK content block (Pydantic model) to a
    plain dict. Required before JSON-serialising the trace because
    ParsedTextBlock / ParsedToolUseBlock aren't JSON-friendly by
    default. Mirrors ``core.planner._content_block_to_dict``."""
    btype = getattr(block, "type", None)
    if btype == "text":
        return {"type": "text", "text": getattr(block, "text", "")}
    if btype == "tool_use":
        return {
            "type": "tool_use",
            "id": getattr(block, "id", ""),
            "name": getattr(block, "name", ""),
            "input": dict(getattr(block, "input", {}) or {}),
        }
    if btype == "thinking":
        # Phase 9B — Sonnet's extended-thinking blocks. The API
        # REQUIRES we preserve both ``thinking`` (the reasoning text)
        # and ``signature`` (HMAC for tamper-evidence) when sending
        # the assistant message back in subsequent iterations, even
        # though the user-facing UI ignores them.
        out: dict[str, Any] = {
            "type": "thinking",
            "thinking": getattr(block, "thinking", ""),
        }
        signature = getattr(block, "signature", None)
        if signature is not None:
            out["signature"] = signature
        return out
    if btype == "redacted_thinking":
        # Encrypted thinking — opaque blob from Anthropic side. Must
        # be forwarded verbatim so the model can decrypt it in the
        # next round.
        return {
            "type": "redacted_thinking",
            "data": getattr(block, "data", ""),
        }
    return {"type": btype or "unknown"}


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


# ---------------------------------------------------------------------------
# Multi-turn agentic chat — Phase 2
# ---------------------------------------------------------------------------
#
# Key differences from the single-shot ``run_agentic_chat`` above:
#
# * Takes a thread_id + new user_text, loads ALL prior turns' traces,
#   concatenates them into the Anthropic messages list. Tool_use and
#   tool_result blocks from earlier turns stay in scope so the agent
#   can reference 'the plate you looked up earlier' without re-calling
#   the skill.
#
# * Compaction layer runs BEFORE each Anthropic call. Trims oversized
#   tool_result content, drops the oldest tool_use/tool_result pairs,
#   and (if still over budget) summarises early turns via an LLM call.
#   Persisted state in chat_turns.trace_json is NEVER mutated — only
#   the in-memory copy fed to the API. Operator's full history stays
#   intact for replay in the UI.
#
# * search_playbooks is always available regardless of which playbook
#   was matched on turn 0. That's how the agent acquires new domain
#   context mid-conversation.
#
# * Per-turn plate detection injects the default lookup skill set if
#   the operator names a plate in the new message. Turn 0 in a thread
#   might be 'general refund question', turn 5 might pivot to a
#   specific plate; we want the skills available on turn 5 too.


_MULTI_TURN_SYSTEM_PROMPT = """\
You are an expert support agent in an ongoing conversation with an
operator. They ask you questions about customer issues; you investigate
with skills and combine real data with playbook knowledge. Be
conversational, not formal. Answer in the same language as the operator.

The conversation history is in scope — you can see every prior turn,
the tools you called, and the results they returned. Use that.

Strict rules:

1. **Don't re-look-up data you already have.** If the operator asks
   "what about that customer's email?" and you looked up the user
   earlier in this conversation, reference the earlier result. Only
   re-call a lookup if the operator explicitly asks you to re-check
   or if the data could plausibly have changed (e.g. transaction
   status of a still-pending payment).

2. **Look up new data when the operator names a specific thing for
   the first time.** Plate, session id, transaction reference,
   customer email — call the relevant lookup before answering.

3. **Use ``search_playbooks`` when the topic drifts.** The originally
   matched playbook was chosen for the first message. If the operator
   pivots to a different domain ("now about B2B invoices..."), search
   for a more relevant playbook before answering. Don't improvise
   from priors when there's a real playbook for the new topic.

4. **Don't fabricate data.** If a lookup returns nothing, say so. "I
   couldn't find anything matching that plate" is a fine answer.
   Never invent a transaction, amount, or session id.

5. **Generic how-to questions don't need skills.** "What's the
   refund process?" — answer from playbook knowledge directly.

6. **Be concise.** 2-5 sentences usually. Lists only when asked.

7. **Match the operator's language.** Croatian in, Croatian out;
   German in, German out; mixed in, lead with whichever language
   dominates.

8. **Cite only real playbook ids.** When you reference a playbook
   inline, use the EXACT id you saw in the initial context block or
   in a ``search_playbooks`` result. Never invent an id that "sounds
   right" — a broken citation is worse than no citation. If you
   aren't sure of an id, omit the citation rather than guess.
"""


# Plate detector — uppercased to match alphanumeric tokens with at
# least one letter AND one digit, length 5-12. Same heuristic as the
# router uses, lifted into the agent so it runs per-turn (turn 5 may
# mention a plate that turn 0 didn't).
_PLATE_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9-]{4,11}\b")

# Same default lookup set as the router's plate fallback. Injected when
# the operator names a plate, regardless of whether the matched
# playbook lists these skills.
_DEFAULT_PLATE_SKILLS = (
    "bmove_user_lookup",
    "skidata_session_lookup",
    "graylog_search",
    "parkis_lookup",
    "datatrans_transaction",
)


def _looks_like_plate(text: str) -> bool:
    for token in _PLATE_TOKEN_RE.findall((text or "").upper()):
        if any(c.isdigit() for c in token) and any(c.isalpha() for c in token):
            return True
    return False


# ---------------------------------------------------------------------------
# Compaction — 5-tier pipeline modelled on Claude Code's approach
# ---------------------------------------------------------------------------
#
# Tier 1 ("snip"): tool_result content blocks for turns older than the
#   most recent N get truncated to first/last 200 chars.
# Tier 2 ("drop tool_results"): if still over budget, drop tool_result
#   content entirely from the oldest turns, keeping tool_use blocks
#   (cheap, preserves call ids for cache hits).
# Tier 3 ("summarise"): if STILL over budget, issue an LLM call that
#   collapses turns 0..K into a single system note. K grows until
#   budget is satisfied.
# Hard floor: keep the last 2 turns verbatim regardless — those are
#   what the agent is actively reasoning about.
#
# The estimate is char/4 (a rough but stable approximation of Anthropic
# tokens — within ~20% for English/CEE text, plenty for budgeting).
# Future polish: swap to ``client.beta.messages.count_tokens`` for an
# exact count, but the round-trip cost is non-trivial and our budget
# is conservative.


# Threshold below which we don't compact at all. 200k window → trigger
# at 160k input tokens (~640k chars). Below that, full history is sent
# verbatim — Claude prefers complete context when it fits.
_COMPACT_THRESHOLD_TOKENS = 160_000

# Floor: never compact within these many trailing turns. The agent is
# usually reasoning about the most recent exchange + maybe one back.
_COMPACT_KEEP_LAST_N_TURNS = 2

# Tier 1 truncate length for old tool_result content (chars).
_COMPACT_TOOL_RESULT_SNIP_CHARS = 400


def _estimate_tokens(messages: list[dict[str, Any]]) -> int:
    """Rough token count via len/4 over serialised JSON. Stable and
    cheap; off by at most ~20%, fine for budget gating."""
    try:
        return len(json.dumps(messages, default=str)) // 4
    except Exception:  # noqa: BLE001
        # Fallback for non-serialisable content blocks — shouldn't
        # happen because every block we construct is dict/str.
        return sum(len(str(m)) // 4 for m in messages)


def _is_tool_use_message(msg: dict[str, Any]) -> bool:
    content = msg.get("content")
    if not isinstance(content, list):
        return False
    return any(
        isinstance(b, dict) and b.get("type") == "tool_use" for b in content
    )


def _is_tool_result_message(msg: dict[str, Any]) -> bool:
    content = msg.get("content")
    if not isinstance(content, list):
        return False
    return any(
        isinstance(b, dict) and b.get("type") == "tool_result" for b in content
    )


def _snip_tool_result_content(content: str | list, max_chars: int) -> Any:
    """Tier 1 snip — truncate verbose tool_result strings. Keeps first
    and last halves so the agent sees both the shape of the response
    and the tail (often the most relevant for chronological data)."""
    if isinstance(content, str):
        if len(content) <= max_chars:
            return content
        half = (max_chars - 20) // 2
        return content[:half] + "\n…[snipped]…\n" + content[-half:]
    if isinstance(content, list):
        out = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if len(text) > max_chars:
                    half = (max_chars - 20) // 2
                    block = {
                        **block,
                        "text": text[:half] + "\n…[snipped]…\n" + text[-half:],
                    }
            out.append(block)
        return out
    return content


def _identify_turn_boundaries(messages: list[dict[str, Any]]) -> list[int]:
    """Return start indices of each operator-perceived turn — every
    string-content user message marks the start of a turn. tool_result
    user messages are NOT turn boundaries; they're inner iterations.
    Used to decide what to drop / summarise without breaking
    tool_use ↔ tool_result pairing."""
    boundaries: list[int] = []
    for i, m in enumerate(messages):
        if m.get("role") != "user":
            continue
        content = m.get("content")
        if isinstance(content, str):
            boundaries.append(i)
    return boundaries


def _compact_messages(
    messages: list[dict[str, Any]],
    *,
    client: Any,
    on_event: EventCallback | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the 5-tier compaction pipeline. Returns (new_messages,
    info_dict). Persisted state is unchanged; only the in-memory list
    passed to the next Anthropic call is compacted.

    The info_dict has keys ``tier`` (0=no-op, 1=snip, 2=drop-tool-results,
    3=summarised), ``before_tokens``, ``after_tokens``, ``dropped_turns``.
    """
    info = {
        "tier": 0,
        "before_tokens": _estimate_tokens(messages),
        "after_tokens": 0,
        "dropped_turns": 0,
        "snipped_tool_results": 0,
    }
    if info["before_tokens"] <= _COMPACT_THRESHOLD_TOKENS:
        info["after_tokens"] = info["before_tokens"]
        return messages, info

    boundaries = _identify_turn_boundaries(messages)
    if len(boundaries) <= _COMPACT_KEEP_LAST_N_TURNS:
        # Single-turn over budget — nothing structural we can drop
        # without breaking pairing. Tier 1 only.
        info["after_tokens"] = info["before_tokens"]
        return messages, info

    # ---- Tier 1: snip old tool_result content ----
    keep_from_idx = boundaries[-_COMPACT_KEEP_LAST_N_TURNS]
    snipped: list[dict[str, Any]] = []
    snip_count = 0
    for i, m in enumerate(messages):
        if i < keep_from_idx and _is_tool_result_message(m):
            new_content = []
            for block in m["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    snipped_content = _snip_tool_result_content(
                        block.get("content", ""),
                        _COMPACT_TOOL_RESULT_SNIP_CHARS,
                    )
                    new_content.append({**block, "content": snipped_content})
                    snip_count += 1
                else:
                    new_content.append(block)
            snipped.append({**m, "content": new_content})
        else:
            snipped.append(m)
    info["snipped_tool_results"] = snip_count
    tokens_after_tier1 = _estimate_tokens(snipped)
    info["tier"] = 1
    if tokens_after_tier1 <= _COMPACT_THRESHOLD_TOKENS:
        info["after_tokens"] = tokens_after_tier1
        if on_event is not None and snip_count > 0:
            on_event(
                "compacted",
                {
                    "tier": info["tier"],
                    "before_tokens": info["before_tokens"],
                    "after_tokens": info["after_tokens"],
                    "dropped_turns": info["dropped_turns"],
                },
            )
        return snipped, info

    # ---- Tier 2: drop the OLDEST turns wholesale ----
    # Keep removing oldest turn until we're under budget OR we'd
    # eat into the keep-floor. Each "turn" here = user msg + the
    # block of inner-iteration messages following it.
    working = snipped
    dropped = 0
    while True:
        bnd = _identify_turn_boundaries(working)
        if len(bnd) <= _COMPACT_KEEP_LAST_N_TURNS + 1:
            break
        # Drop everything from start of working until index of 2nd turn boundary
        drop_until = bnd[1]
        working = working[drop_until:]
        dropped += 1
        if _estimate_tokens(working) <= _COMPACT_THRESHOLD_TOKENS:
            break
    info["dropped_turns"] = dropped
    info["tier"] = 2 if dropped > 0 else info["tier"]
    tokens_after_tier2 = _estimate_tokens(working)
    if tokens_after_tier2 <= _COMPACT_THRESHOLD_TOKENS:
        info["after_tokens"] = tokens_after_tier2
        if on_event is not None and info["tier"] >= 1:
            on_event(
                "compacted",
                {
                    "tier": info["tier"],
                    "before_tokens": info["before_tokens"],
                    "after_tokens": info["after_tokens"],
                    "dropped_turns": info["dropped_turns"],
                },
            )
        return working, info

    # ---- Tier 3: LLM summarisation of remaining old turns ----
    # We're still over budget, even after dropping old turns. This is
    # an extreme case (>40 substantive turns in one thread). Issue a
    # single summarisation call to collapse the oldest section.
    bnd = _identify_turn_boundaries(working)

    def _emit_compacted() -> None:
        if on_event is not None and info["tier"] >= 1:
            on_event(
                "compacted",
                {
                    "tier": info["tier"],
                    "before_tokens": info["before_tokens"],
                    "after_tokens": info["after_tokens"],
                    "dropped_turns": info["dropped_turns"],
                },
            )

    if len(bnd) <= _COMPACT_KEEP_LAST_N_TURNS + 1:
        info["after_tokens"] = tokens_after_tier2
        _emit_compacted()
        return working, info
    keep_from = bnd[-_COMPACT_KEEP_LAST_N_TURNS]
    older = working[:keep_from]
    keepers = working[keep_from:]
    try:
        summary_text = _summarise_history(older, client=client)
    except Exception:  # noqa: BLE001
        # Summarisation failed — fall back to Tier 2 output. Still
        # emit so the UI surfaces that compaction happened.
        info["after_tokens"] = tokens_after_tier2
        _emit_compacted()
        return working, info
    synthetic = [
        {
            "role": "user",
            "content": (
                "[Summary of earlier conversation, compacted to fit the "
                "context window. Refer to this rather than asking the "
                "operator to repeat themselves.]\n\n" + summary_text
            ),
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Understood — I'll continue from there.",
                }
            ],
        },
    ]
    final = synthetic + keepers
    info["tier"] = 3
    info["after_tokens"] = _estimate_tokens(final)
    if on_event is not None:
        on_event(
            "compacted",
            {
                "tier": info["tier"],
                "before_tokens": info["before_tokens"],
                "after_tokens": info["after_tokens"],
                "dropped_turns": info["dropped_turns"],
            },
        )
    return final, info


def _summarise_history(
    messages: list[dict[str, Any]], *, client: Any
) -> str:
    """Issue one Anthropic call to summarise an old slice of the
    conversation. Returns plain text. Used by Tier 3 compaction only —
    we don't summarise unless we have to (expensive token-wise).

    The summary instruction lives in a system prompt; the slice is
    sent as a single user message with a synthetic preamble. We
    explicitly ask for tool-result preservation (amounts, plates,
    session ids) because that's the data the agent will need to
    reference downstream.
    """
    serialised = json.dumps(messages, default=str)
    if len(serialised) > 200_000:
        # Even the slice is too big — pre-truncate so the summary
        # call itself doesn't OOM.
        serialised = serialised[:200_000]
    resp = _with_anthropic_retries(lambda: client.messages.create(
        model=config.CHAT_MODEL,
        max_tokens=1500,
        system=(
            "You are a context-compaction step in a multi-turn agentic "
            "chat. The user will paste a JSON-serialised slice of the "
            "early conversation. Produce a SHORT bullet summary (≤10 "
            "bullets, ≤500 words total) that preserves: (a) every "
            "concrete data point the agent looked up (plates, amounts, "
            "session ids, customer emails, transaction statuses), (b) "
            "the operator's intent through that section, (c) any "
            "open questions or unresolved threads. Drop greetings, "
            "filler, and conversational scaffolding. Output bullets "
            "only, no preamble."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    "Slice of earlier conversation to summarise:\n\n"
                    + serialised
                ),
            }
        ],
    ))
    text_parts = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(getattr(block, "text", ""))
    return "".join(text_parts).strip() or "[Earlier conversation summarised.]"


# ---------------------------------------------------------------------------
# Phase 9C — citation self-correction.
# ---------------------------------------------------------------------------
#
# When the agent's final answer cites a playbook id that doesn't exist
# in the corpus (a hallucination), we issue one corrective Anthropic
# call asking it to rewrite without the invalid ids. This is a
# post-hoc safety net on top of system-prompt rule #8 — the rule
# catches most cases, the rewrite handles the rest. Capped at one
# correction round to avoid loops if the model is being stubborn.


_CITATION_RE = re.compile(r"\[([A-Za-z0-9][A-Za-z0-9_-]+)\]")


def self_correct_citations(
    original_text: str,
    valid_ids: set[str],
    *,
    client: Any = None,
    max_tokens: int = 1500,
) -> tuple[str, list[str]]:
    """If ``original_text`` cites any id NOT in ``valid_ids``, issue
    one Anthropic call to rewrite it without those invalid citations.
    Returns ``(corrected_text, invalid_ids_found)``. When no
    hallucinated ids are present, returns the original text unchanged
    and an empty list — no LLM call is made.

    The caller is responsible for passing the union of "every playbook
    id known to the index" so this function can compare blindly. We
    do NOT verify whether a cited id was actually in the top-K shown
    to the model — that's a stricter test the caller can layer on if
    desired.
    """
    cited = set(_CITATION_RE.findall(original_text or ""))
    invalid = sorted(cited - valid_ids)
    if not invalid:
        return original_text, []
    if client is None:
        if not config.ANTHROPIC_API_KEY:
            # No API key — return original; we can't fix.
            return original_text, invalid
        from anthropic import Anthropic

        client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    invalid_list = ", ".join(f"[{cid}]" for cid in invalid)
    correction_system = (
        "You are a context-editing assistant. The user will paste an "
        "answer that contains some invalid inline citations (playbook "
        "ids that don't exist in the corpus). Rewrite the answer "
        "preserving its meaning, tone, and language, but DELETE the "
        "invalid citation tokens entirely. Keep all valid citations "
        "untouched. Do not add new citations. Do not add explanations "
        "or apologies — just return the corrected text verbatim."
    )
    user_msg = (
        f"Invalid citations to remove: {invalid_list}\n\n"
        f"Original answer:\n\n{original_text}"
    )
    try:
        resp = _with_anthropic_retries(lambda: client.messages.create(
            model=config.CHAT_MODEL,
            max_tokens=max_tokens,
            system=correction_system,
            messages=[{"role": "user", "content": user_msg}],
        ))
    except Exception:  # noqa: BLE001
        # Correction failed — leave original; UI will mark hallucinated
        # ids as broken citations.
        return original_text, invalid
    text_parts = []
    for block in resp.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(getattr(block, "text", ""))
    corrected = "".join(text_parts).strip()
    if not corrected:
        return original_text, invalid
    return corrected, invalid


# ---------------------------------------------------------------------------
# Multi-turn entry point
# ---------------------------------------------------------------------------


@dataclass
class ChatTurnResult:
    """What ``run_agentic_turn`` returns after the loop terminates."""
    turn_id: int
    answer: str
    iterations: int
    skills_called: list[str]
    compaction_info: dict[str, Any] | None = None


def run_agentic_turn(
    *,
    thread_id: int,
    user_text: str,
    initial_playbook: Playbook,
    on_event: EventCallback,
    client: Any = None,
    turn_id: int | None = None,
) -> ChatTurnResult:
    """Outer entry point — wraps the actual loop in a top-level OTEL
    span so every metric / log line emitted inside is attached to the
    right trace. Thin wrapper; all the work happens in
    ``_run_agentic_turn_impl``."""
    with _tracer.start_as_current_span("chat.turn") as span:
        span.set_attribute("chat.thread_id", thread_id)
        if turn_id is not None:
            span.set_attribute("chat.turn_id", turn_id)
        try:
            result = _run_agentic_turn_impl(
                thread_id=thread_id,
                user_text=user_text,
                initial_playbook=initial_playbook,
                on_event=on_event,
                client=client,
                turn_id=turn_id,
            )
            span.set_attribute("chat.iterations", result.iterations)
            span.set_attribute(
                "chat.skills_called_count", len(result.skills_called)
            )
            return result
        except Exception as exc:
            span.record_exception(exc)
            raise


def _run_agentic_turn_impl(
    *,
    thread_id: int,
    user_text: str,
    initial_playbook: Playbook,
    on_event: EventCallback,
    client: Any = None,
    turn_id: int | None = None,
) -> ChatTurnResult:
    """Append a new turn to an existing thread, run the agentic loop
    with the full prior conversation in context, persist the result.

    ``initial_playbook`` is the domain context for turn 0 — caller
    retrieves top-K and passes #1. Subsequent turns reuse the priors
    naturally through trace concatenation; if topic shifts, the agent
    calls search_playbooks to discover a new playbook.

    ``turn_id`` is optional. When passed, the caller has already
    inserted the pending turn row (typical for HTTP handlers that
    need the row to exist before spawning the SSE tail); we use it
    in-place. When omitted, we create the row ourselves (CLI / test
    paths that don't need pre-allocation).

    Always-available skills: every skill in the playbook's allowed_skills
    (read-only filter applied), plus the universal ``search_playbooks``,
    plus the default lookup set when the new user_text contains a
    plate-shaped token.
    """
    if client is None:
        if not config.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        from anthropic import Anthropic

        client = Anthropic(api_key=config.ANTHROPIC_API_KEY)

    if turn_id is not None:
        # Caller already inserted the row (HTTP daemon path) — just
        # load it. Avoid double-create which would orphan the empty
        # original and leave the SSE tail attached to the wrong id.
        existing = chat_threads.get_turn(turn_id)
        if existing is None:
            raise ValueError(f"turn_id {turn_id} not found")
        turn = existing
    else:
        turn = chat_threads.create_pending_turn(
            thread_id=thread_id, user_text=user_text
        )

    # Load prior turns and concat their traces into the working
    # messages list. Prior tool_use ↔ tool_result blocks are kept
    # intact so the agent can reference them.
    prior_turns = chat_threads.list_turns_for_thread(thread_id)
    prior_messages: list[dict[str, Any]] = []
    for prior in prior_turns:
        if prior.id == turn.id:
            continue  # current turn — its trace is built below
        prior_messages.extend(prior.trace or [])

    # Build the initial prompt for this turn. On turn 0 we include the
    # full playbook body as domain context (same as single-shot agentic
    # chat). On later turns the playbook context is already in scope
    # from turn 0; we just append the new user message verbatim.
    is_first_turn = len(prior_messages) == 0
    if is_first_turn:
        new_user_msg = {
            "role": "user",
            "content": _build_initial_prompt(user_text, initial_playbook),
        }
    else:
        new_user_msg = {"role": "user", "content": user_text}

    # This turn's contribution to the conversation — what we'll store
    # as ``trace_json`` on the chat_turns row. Starts with the user
    # message; the loop appends assistant turns + tool_result user
    # messages as they happen.
    this_turn_trace: list[dict[str, Any]] = [new_user_msg]

    # Tool list: playbook-allowed read skills + universal
    # search_playbooks + plate defaults if applicable.
    base_skills = list(initial_playbook.metadata.get("allowed_skills") or [])
    if _looks_like_plate(user_text):
        for s in _DEFAULT_PLATE_SKILLS:
            if s not in base_skills:
                base_skills.append(s)
    # search_playbooks is always available in chat — it's how the
    # agent escapes the initial playbook when the topic drifts.
    if "search_playbooks" not in base_skills:
        base_skills.append("search_playbooks")
    tools = chat_tools_for_playbook(base_skills)
    if not tools:
        # Defensive — every chat thread has search_playbooks at
        # minimum so this shouldn't happen. Bail out with a clear
        # error rather than calling Anthropic with no tools.
        chat_threads.update_turn(
            turn.id, status="error", error_message="no chat skills available"
        )
        return ChatTurnResult(
            turn_id=turn.id, answer="", iterations=0, skills_called=[]
        )

    # Persist event_handler that ALSO appends to the persisted
    # events_json on each emit, so refresh mid-stream finds skill
    # rows in chronological order.
    events_persisted: list[dict[str, Any]] = []

    # Phase 14 — live token persistence. The SSE tail in the router
    # streams ``final_assistant_text`` deltas to the client by polling
    # the DB row. Without partial persistence, the column wouldn't
    # update until the iteration ends — leaving the operator staring
    # at an intro line while iteration 2 silently fills in the body.
    # Throttle to ~100ms so we batch tokens without flooding SQLite.
    _partial_text = [""]  # current iteration's in-progress text
    _last_partial_persist = [_time_mod.monotonic()]
    _PARTIAL_FLUSH_INTERVAL_S = 0.1

    def _flush_partial(force: bool = False) -> None:
        """Write the current visible text (committed iterations +
        in-flight iteration's tokens so far) to
        ``chat_turns.final_assistant_text`` so the SSE tail can pick
        it up. ``force`` bypasses the throttle — used at iteration
        boundaries so the operator sees the last word before the
        next tool call kicks in."""
        if not _partial_text[0]:
            return
        now = _time_mod.monotonic()
        if not force and now - _last_partial_persist[0] < _PARTIAL_FLUSH_INTERVAL_S:
            return
        _last_partial_persist[0] = now
        live_text = (
            final_answer + ("\n\n" if final_answer else "") + _partial_text[0]
        )
        try:
            chat_threads.update_turn(
                turn.id, final_assistant_text=live_text
            )
        except Exception:  # noqa: BLE001
            pass

    def _wrapped_on_event(kind: str, payload: dict[str, Any]) -> None:
        on_event(kind, payload)
        if kind == "token":
            text = payload.get("text") or ""
            if text:
                _partial_text[0] += text
                _flush_partial()
            return
        events_persisted.append({"type": kind, **payload})
        try:
            chat_threads.update_turn(
                turn.id, events=events_persisted
            )
        except Exception:  # noqa: BLE001
            pass

    # Combined messages list for the API. Compaction runs on this
    # before every Anthropic call.
    messages = prior_messages + this_turn_trace
    final_answer = ""
    skills_called: list[str] = []
    composing_emitted = False
    last_compaction_info: dict[str, Any] | None = None
    # Phase 9D — token + cost accumulator. Each Anthropic call's
    # ``usage`` is added in; the final totals get persisted on the
    # chat_turns row so the UI can render a per-turn cost footer.
    total_input_tokens = 0
    total_output_tokens = 0

    import time as _time

    # Phase 12.6 — turn-duration timer. Wall-clock; resets per turn.
    _turn_started_at = _time.time()

    for iteration in range(1, _MAX_ITERATIONS + 1):
        # ---- Interrupt gate ----
        # Operator hit Stop / pressed ESC: exit cleanly, persist a
        # cancellation marker the UI can detect. The current Anthropic
        # call has already ended for the previous iteration so no
        # in-flight stream is leaking; the next iteration just doesn't
        # start. Worst-case latency ≈ one Claude call (~5-15s).
        if _consume_interrupt(turn.id):
            chat_threads.update_turn(
                turn.id,
                trace=this_turn_trace,
                final_assistant_text=final_answer,
                events=events_persisted,
                status="error",
                error_message=INTERRUPT_ERROR_PREFIX,
            )
            CHAT_TURNS_TOTAL.labels(status="interrupted").inc()
            CHAT_TURN_DURATION.observe(_time.time() - _turn_started_at)
            return ChatTurnResult(
                turn_id=turn.id,
                answer=final_answer,
                iterations=iteration - 1,
                skills_called=skills_called,
                compaction_info=last_compaction_info,
            )

        # ---- Compaction gate ----
        messages, c_info = _compact_messages(
            messages, client=client, on_event=_wrapped_on_event
        )
        if c_info.get("tier", 0) > 0:
            last_compaction_info = c_info
            CHAT_COMPACTION_HITS.labels(tier=str(c_info.get("tier"))).inc()

        # ---- Heartbeat ----
        # Anthropic's stream can take several seconds to first byte
        # (especially after tool_result rounds). Emit a 'thinking'
        # event so the UI shows continuous activity instead of a
        # silent gap between skills and the next text stream.
        _wrapped_on_event("thinking", {"iteration": iteration})

        # Phase 9B — extended thinking. When budget > 0 we ask Sonnet
        # to think in a dedicated channel before answering. The SDK
        # streams these as ``thinking_delta`` blocks. They're separate
        # from text_delta and we route them to a new ``thinking_text``
        # event so the UI can render them as a collapsible quote above
        # the final prose. Thinking tokens count toward output billing
        # (already captured by usage accounting).
        stream_kwargs: dict[str, Any] = {
            "model": config.CHAT_MODEL,
            "max_tokens": (
                config.CHAT_MAX_TOKENS + config.CHAT_THINKING_BUDGET
            ),
            "system": _MULTI_TURN_SYSTEM_PROMPT,
            "messages": messages,
            "tools": tools,
        }
        if config.CHAT_THINKING_BUDGET > 0:
            stream_kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": config.CHAT_THINKING_BUDGET,
            }

        with client.messages.stream(**stream_kwargs) as stream:
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
                    elif block.type == "thinking":
                        # Thinking block start — no setup needed; the
                        # deltas will be forwarded directly as
                        # ``thinking_text`` events.
                        pass
                    elif block.type == "tool_use":
                        current_tool = {
                            "id": block.id,
                            "name": block.name,
                            "input_buffer": "",
                        }
                elif etype == "content_block_delta":
                    delta = event.delta
                    dtype = getattr(delta, "type", None)
                    if dtype == "thinking_delta":
                        # Sonnet's extended-thinking channel. We forward
                        # the text to the UI but do NOT add it to
                        # text_buffers / current_text_block; the
                        # operator's chat bubble should only contain
                        # the final answer.
                        _wrapped_on_event(
                            "thinking_text",
                            {"text": getattr(delta, "thinking", "")},
                        )
                    elif dtype == "text_delta":
                        if not composing_emitted:
                            _wrapped_on_event("composing", {})
                            composing_emitted = True
                        _wrapped_on_event("token", {"text": delta.text})
                        current_text_block += delta.text
                    elif dtype == "input_json_delta":
                        if current_tool is not None:
                            current_tool["input_buffer"] += delta.partial_json
                elif etype == "content_block_stop":
                    if current_tool is not None:
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
            final_msg = stream.get_final_message()

        # Phase 9D — accumulate Anthropic usage from each iteration's
        # final_message. ``usage`` is a Pydantic model on the SDK side
        # with input_tokens / output_tokens attrs.
        try:
            usage = getattr(final_msg, "usage", None)
            if usage is not None:
                total_input_tokens += int(
                    getattr(usage, "input_tokens", 0) or 0
                )
                total_output_tokens += int(
                    getattr(usage, "output_tokens", 0) or 0
                )
        except Exception:  # noqa: BLE001
            # Don't let cost accounting break a successful turn.
            pass

        # Phase 10 — hard cost cap. If we've spent past the per-turn
        # ceiling, abort cleanly: persist what we have, mark error
        # with an unambiguous marker so the UI can render a 'cap
        # reached' notice rather than a generic crash. Capped turns
        # never enter the next iteration, so even a stuck loop can't
        # spiral.
        running_cost = _estimate_cost_usd(
            total_input_tokens, total_output_tokens
        )
        cap = config.CHAT_TURN_COST_CAP_USD
        if cap > 0 and running_cost >= cap:
            usage_summary = {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cost_usd": round(running_cost, 6),
                "capped": True,
            }
            chat_threads.update_turn(
                turn.id,
                trace=this_turn_trace,
                final_assistant_text=final_answer
                or "(Turn aborted before any text was produced.)",
                events=events_persisted,
                usage=usage_summary,
                status="error",
                error_message=(
                    f"{COST_CAP_ERROR_PREFIX}: "
                    f"${running_cost:.4f} >= cap ${cap:.4f}"
                ),
            )
            CHAT_COST_CAP_HITS.labels(scope="turn").inc()
            CHAT_TURNS_TOTAL.labels(status="capped").inc()
            CHAT_TURN_COST.observe(running_cost)
            CHAT_TURN_DURATION.observe(_time.time() - _turn_started_at)
            return ChatTurnResult(
                turn_id=turn.id,
                answer=final_answer,
                iterations=iteration,
                skills_called=skills_called,
                compaction_info=last_compaction_info,
            )

        # Convert SDK content blocks to plain dicts so trace_json
        # serialises cleanly. SDK ParsedTextBlock / ParsedToolUseBlock
        # are Pydantic models that json.dumps can't handle by default.
        assistant_content_dicts = [
            _block_to_dict(b) for b in final_msg.content
        ]
        assistant_message = {
            "role": "assistant",
            "content": assistant_content_dicts,
        }
        messages.append(assistant_message)
        this_turn_trace.append(assistant_message)
        # Phase 14 — accumulate iteration text CUMULATIVELY. Each
        # iteration's text is appended to the prior, so the operator
        # sees the agent's intro line (iter 1), the report (iter 2),
        # and any follow-up commentary in chronological order. The
        # earlier behaviour of replacing ``final_answer`` on each
        # iteration meant iter 1's intro disappeared the moment iter
        # 2 had text — and worse, the partial text the SSE tail had
        # already streamed to the client would be silently overridden
        # by an entirely different string, breaking the delta-by-prefix
        # invariant.
        accumulated_text = "".join(text_buffers)
        if accumulated_text:
            if final_answer:
                final_answer = final_answer + "\n\n" + accumulated_text
            else:
                final_answer = accumulated_text
        # Reset the in-flight buffer — the iteration's text just got
        # baked into ``final_answer``. Don't reset _last_partial_persist:
        # next iteration's first flush should still respect the throttle.
        _partial_text[0] = ""
        try:
            chat_threads.update_turn(
                turn.id,
                trace=this_turn_trace,
                final_assistant_text=final_answer,
            )
        except Exception:  # noqa: BLE001
            pass

        if not tool_uses:
            usage_summary = {
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "cost_usd": round(
                    _estimate_cost_usd(total_input_tokens, total_output_tokens),
                    6,
                ),
            }
            chat_threads.update_turn(
                turn.id,
                trace=this_turn_trace,
                final_assistant_text=final_answer,
                events=events_persisted,
                usage=usage_summary,
                status="done",
            )
            CHAT_TURNS_TOTAL.labels(status="done").inc()
            CHAT_TURN_COST.observe(usage_summary["cost_usd"])
            CHAT_TURN_DURATION.observe(_time.time() - _turn_started_at)
            return ChatTurnResult(
                turn_id=turn.id,
                answer=final_answer,
                iterations=iteration,
                skills_called=skills_called,
                compaction_info=last_compaction_info,
            )

        # Phase 9A — parallel tool dispatch. Claude can emit multiple
        # ``tool_use`` blocks in one assistant turn (e.g. plate lookup
        # + Datatrans transaction in parallel). Submitting all of them
        # to the executor before awaiting any cuts a multi-skill turn
        # from N×latency down to roughly max(latencies). We still
        # emit ``skill_executing`` events in tool order so the UI
        # timeline reads naturally; the awaits happen in the same
        # order so ``skill_executed`` events come out predictably too.
        tool_results: list[dict[str, Any]] = []
        submitted: list[tuple[dict[str, Any], float, Any, str | None]] = []
        for tu in tool_uses:
            name = tu["name"]
            params = tu["input"]
            call_id = tu["id"]
            skills_called.append(name)
            _wrapped_on_event(
                "skill_executing",
                {"skill": name, "params": params, "call_id": call_id},
            )
            started = _time.time()
            future, immediate_err = _submit_skill(name, params)
            submitted.append((tu, started, future, immediate_err))

        for tu, started, future, immediate_err in submitted:
            name = tu["name"]
            params = tu["input"]
            call_id = tu["id"]
            if future is None:
                ok, result_data, err = False, None, immediate_err
            else:
                ok, result_data, err = _await_skill(future, name)
            elapsed_ms = int((_time.time() - started) * 1000)
            CHAT_SKILL_DURATION.labels(
                skill=name, ok=str(bool(ok)).lower()
            ).observe(elapsed_ms / 1000.0)
            _wrapped_on_event(
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
            if ok and result_data is not None:
                payload = _safe_dumps(result_data)
            else:
                payload = _safe_dumps({"error": err or "unknown_error"})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call_id,
                    "content": payload,
                }
            )

        user_tool_results_msg = {"role": "user", "content": tool_results}
        messages.append(user_tool_results_msg)
        this_turn_trace.append(user_tool_results_msg)

    # Iteration cap — persist what we have and flag.
    usage_summary = {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "cost_usd": round(
            _estimate_cost_usd(total_input_tokens, total_output_tokens),
            6,
        ),
    }
    chat_threads.update_turn(
        turn.id,
        trace=this_turn_trace,
        final_assistant_text=final_answer
        or "(Agent reached the iteration cap without producing a final answer.)",
        events=events_persisted,
        usage=usage_summary,
        status="done",
    )
    CHAT_TURNS_TOTAL.labels(status="done").inc()
    CHAT_TURN_COST.observe(usage_summary["cost_usd"])
    CHAT_TURN_DURATION.observe(_time.time() - _turn_started_at)
    return ChatTurnResult(
        turn_id=turn.id,
        answer=final_answer or "(iter cap)",
        iterations=_MAX_ITERATIONS,
        skills_called=skills_called,
        compaction_info=last_compaction_info,
    )
