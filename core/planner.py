"""Agent loop — drives Claude tool_use to actually execute skills.

Two entrypoints:

- ``run(ticket, playbook)`` → start a fresh planning session
- ``resume(action_id, approved, edited_input)`` → continue after HITL decision

The planner is the writer for any playbook with ``allowed_skills``. It
runs INSTEAD of the drafter (not after it) — ``core.agent_runner`` picks
exactly one writer per ticket based on the matched playbook. The planner
reads the playbook's ``allowed_skills``, hands Claude only the matching
tool specs, then processes whatever ``tool_use`` Claude returns:

- read skill                                      → execute, feed result back
- write skill, mode=shadow                        → log, fake-result, feed back
- write skill, mode=assisted                      → save pending action, pause
- write skill, mode=autonomous + playbook opts-in → execute, feed back
- write skill, mode=autonomous + no opt-in        → save pending action, pause

Iteration cap is ``config.PLANNER_MAX_ITERATIONS`` so a confused model
can't burn the budget.
"""
from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Sequence

import config

log = logging.getLogger(__name__)
from core import agent_audit, agent_config, pending_actions
from core.retrieval import Playbook, load_playbook
from core.skills.registry import REGISTRY, get_skill, tools_for_playbook
from core.skills.validator import validate


_SYSTEM_PROMPT = """\
You are an agent helping a parking-company support team resolve a customer ticket.

You have been given:
- The ticket (summary, description, customer language signal)
- The matched playbook describing what to do for this type of problem

YOUR JOB is to investigate the customer's claim with the source-of-truth
systems FIRST, then post ONE public reply that is grounded in what those
systems actually show. You are the sole writer for this ticket — there
is no pre-drafted reply to fall back on.

Strict rules — read carefully:

1. **MANDATORY BASELINE LOOKUPS.** For every ticket where they are in
   your tool list, you MUST call BOTH ``bmove_user_lookup`` AND
   ``graylog_search`` before composing your public reply. These two are
   the non-negotiable baseline — they tell you who the account is and
   what the systems logged. Additional lookups
   (``skidata_session_lookup``, ``parkis_lookup``,
   ``datatrans_transaction``) are optional and should be added based on
   what the ticket actually mentions (garage session, SMS/parking
   ticket, payment dispute respectively).

2. **VERIFY BEFORE YOU WRITE.** Before you call ``jira_add_public_comment``
   for the first time on this ticket, the baseline lookups above must
   have run. Never reply based on what the customer claims alone; always
   check the data first. Extract the plate, session id, or transaction
   reference from the ticket and look it up. If multiple tools could
   corroborate (e.g. ``datatrans_transaction`` AND ``graylog_search``),
   prefer to call both.

3. **Ground your reply in the lookup results.** The public comment you
   draft must reflect what the systems actually returned — confirm the
   payment if it settled, acknowledge the failure if it failed, ask for
   more details only if no system has data on this plate/session.

4. **One public comment is usually enough.** After you successfully post
   the public reply, END YOUR TURN with a brief summary. Do not propose
   further actions unless the playbook prose for THIS ticket explicitly
   says you must (e.g. "after replying, change status to X").

5. **Status transitions are EXCEPTIONAL, not default.** Do not call
   ``jira_transition`` just because it's available. Only call it if the
   playbook explicitly tells you to move the ticket to a specific
   status FOR THIS TICKET TYPE. The default behaviour is: leave the
   status alone and let the operator decide.

6. **Internal notes are for handoffs, not bookkeeping.** Only call
   ``jira_add_internal_comment`` if the playbook says you should tag a
   colleague or record specific handoff context. Do not log "I sent the
   reply" — the audit trail already captures that.

7. **Reading is free; writing is not.** Verification lookups
   (graylog/datatrans/bmove/parkis/skidata/get_history) are safe to call
   eagerly. Don't call the SAME lookup with the same params twice.

8. **If a write fails, try ONCE more with corrected params.** If it
   fails again, end your turn — don't keep retrying.

9. Match the customer's language for public comments.

10. Never ask the operator for permission in your text response — the
   system handles approvals automatically based on tool risk.\
"""


@dataclass(frozen=True)
class PlannerResult:
    """Outcome of one ``run()`` / ``resume()`` invocation.

    status:
        - ``done``                → Claude ended its turn cleanly
        - ``awaiting_approval``   → a write tool needs operator decision
        - ``failed``              → validator rejected everything / API error
        - ``max_iterations``      → burned through ``PLANNER_MAX_ITERATIONS``
    """

    status: str
    pending_action_id: str | None = None
    error: str | None = None
    iterations: int = 0
    summary: str | None = None  # final assistant text if status == 'done'


# ---------------------------------------------------------------------------
# Public entrypoints
# ---------------------------------------------------------------------------


def run(
    *,
    ticket: dict[str, Any],
    playbook: Playbook,
    client=None,
) -> PlannerResult:
    """Start a fresh planner loop for one ticket."""
    mode = agent_config.effective_mode(playbook.id)
    tools = tools_for_playbook(playbook.metadata.get("allowed_skills") or [])
    if not tools:
        # Playbook has no skills wired up — planner is a no-op for it.
        return PlannerResult(status="done", iterations=0)

    # Discard any pending rows left over from a previous run of THIS
    # ticket — their messages_blob references a stale loop. Without
    # this each re-process piles another paused tool_use on top and
    # the inbox shows N duplicates of the same draft reply.
    ticket_id = str(ticket.get("key") or ticket.get("ticket_id") or "")
    if ticket_id:
        pending_actions.clear_for_ticket(ticket_id)

    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": _build_initial_prompt(ticket, playbook),
        }
    ]
    return _loop(
        client=client,
        messages=messages,
        playbook=playbook,
        ticket=ticket,
        mode=mode,
        iteration=0,
        tools=tools,
    )


def resume(
    *,
    action_id: str,
    approved: bool,
    edited_input: dict[str, Any] | None = None,
    rejection_note: str | None = None,
    decided_by: str | None = None,
    playbooks: Sequence[Playbook] | None = None,
    client=None,
) -> PlannerResult:
    """Continue a planner loop that paused on HITL.

    Loads the snapshot, builds a ``tool_result`` for the decision the
    operator made, deletes the pending row, and re-enters the loop. The
    optional ``playbooks`` list lets the backend pass the already-loaded
    corpus to avoid disk re-read; falls back to a glob.
    """
    pa = pending_actions.get(action_id)
    if pa is None:
        return PlannerResult(
            status="failed", error=f"pending_action {action_id} not found"
        )

    playbook = _find_playbook(pa.playbook_id, playbooks)
    if playbook is None:
        return PlannerResult(
            status="failed", error=f"playbook {pa.playbook_id} not on disk"
        )

    tools = tools_for_playbook(playbook.metadata.get("allowed_skills") or [])

    # Build the tool_result that closes out the paused tool_use.
    if approved:
        params = dict(edited_input) if edited_input is not None else pa.skill_input
        skill = get_skill(pa.skill_name)
        if skill is None:
            tool_result = _tool_result_error(
                pa.tool_use_id, f"skill {pa.skill_name} not registered"
            )
            agent_audit.record(
                ticket_id=pa.ticket_id,
                playbook_id=pa.playbook_id,
                skill_name=pa.skill_name,
                skill_input=params,
                outcome="approved",
                ok=False,
                error=f"skill {pa.skill_name} not registered",
                decided_by=decided_by,
                mode=pa.mode,
                iteration=pa.iteration,
            )
        else:
            try:
                result = skill.execute(**params)
            except Exception as exc:  # noqa: BLE001
                tool_result = _tool_result_error(
                    pa.tool_use_id, f"skill_crashed: {exc}"
                )
                agent_audit.record(
                    ticket_id=pa.ticket_id,
                    playbook_id=pa.playbook_id,
                    skill_name=pa.skill_name,
                    skill_input=params,
                    outcome="approved",
                    ok=False,
                    error=f"skill_crashed: {exc}",
                    decided_by=decided_by,
                    mode=pa.mode,
                    iteration=pa.iteration,
                )
            else:
                tool_result = _tool_result_from(pa.tool_use_id, result)
                agent_audit.record(
                    ticket_id=pa.ticket_id,
                    playbook_id=pa.playbook_id,
                    skill_name=pa.skill_name,
                    skill_input=params,
                    outcome="approved",
                    ok=result.ok,
                    result_data=result.data if result.ok else None,
                    error=result.error if not result.ok else None,
                    decided_by=decided_by,
                    mode=pa.mode,
                    iteration=pa.iteration,
                )
    else:
        tool_result = _tool_result_error(
            pa.tool_use_id,
            f"Operator rejected this action. "
            f"Reason: {rejection_note or 'no reason given'}. "
            "Try a different approach or end the turn.",
        )
        agent_audit.record(
            ticket_id=pa.ticket_id,
            playbook_id=pa.playbook_id,
            skill_name=pa.skill_name,
            skill_input=pa.skill_input,
            outcome="rejected",
            ok=False,
            error=rejection_note or "no reason given",
            decided_by=decided_by,
            mode=pa.mode,
            iteration=pa.iteration,
        )

    messages = list(pa.messages_blob)
    # Combine the partial results captured at pause-time with the
    # operator's just-resolved tool_result. ALL blocks from the
    # assistant turn must now be paired.
    full_user_content = list(pa.partial_tool_results) + [tool_result]
    messages.append({"role": "user", "content": full_user_content})

    pending_actions.delete(action_id)

    fake_ticket = {"key": pa.ticket_id}
    return _loop(
        client=client,
        messages=messages,
        playbook=playbook,
        ticket=fake_ticket,
        mode=pa.mode,
        iteration=pa.iteration,
        tools=tools,
    )


# ---------------------------------------------------------------------------
# Core loop
# ---------------------------------------------------------------------------


def _loop(
    *,
    client,
    messages: list[dict[str, Any]],
    playbook: Playbook,
    ticket: dict[str, Any],
    mode: str,
    iteration: int,
    tools: list[dict[str, Any]],
) -> PlannerResult:
    client = _get_client(client)

    while iteration < config.PLANNER_MAX_ITERATIONS:
        # Hard cap on successful writes — protects against a confused
        # model that keeps grinding new write attempts after the
        # primary action is done (the comment was sent, the playbook is
        # satisfied, but Claude keeps proposing transitions/labels).
        # Failed writes don't count, so genuine recovery from a single
        # transient error is still allowed.
        if _count_successful_writes(messages) >= config.PLANNER_MAX_WRITE_ACTIONS:
            return PlannerResult(
                status="done",
                iterations=iteration,
                summary=(
                    f"Reached PLANNER_MAX_WRITE_ACTIONS"
                    f"={config.PLANNER_MAX_WRITE_ACTIONS}; stopping."
                ),
            )
        iteration += 1
        try:
            response = _create_with_retry(
                client,
                model=config.PLANNER_MODEL,
                max_tokens=config.PLANNER_MAX_TOKENS,
                system=_SYSTEM_PROMPT,
                tools=tools,
                messages=messages,
            )
        except Exception as exc:  # noqa: BLE001
            return PlannerResult(
                status="failed",
                error=f"anthropic_error: {exc}",
                iterations=iteration,
            )

        # Snapshot assistant turn as plain dicts so future resumes can
        # re-send the conversation without owning SDK objects.
        assistant_content = [_content_block_to_dict(b) for b in response.content]
        messages.append({"role": "assistant", "content": assistant_content})

        if response.stop_reason == "end_turn":
            return PlannerResult(
                status="done",
                iterations=iteration,
                summary=_last_text(response.content),
            )

        if response.stop_reason != "tool_use":
            return PlannerResult(
                status="failed",
                error=f"unexpected_stop_reason: {response.stop_reason}",
                iterations=iteration,
            )

        tool_results: list[dict[str, Any]] = []
        for block in response.content:
            if getattr(block, "type", None) != "tool_use":
                continue

            vr = validate(block.name, playbook.metadata, mode)
            if not vr.ok:
                tool_results.append(
                    _tool_result_error(block.id, f"validator: {vr.reason}")
                )
                continue

            skill = get_skill(block.name)

            # Shadow mode never executes writes; reads still run (harmless).
            if mode == "shadow" and (skill is None or skill.is_write):
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": (
                            f"[SHADOW MODE] Would have called "
                            f"{block.name}({_compact(block.input)}). No effect."
                        ),
                    }
                )
                _safe_audit(
                    ticket=ticket,
                    playbook_id=playbook.id,
                    skill_name=block.name,
                    skill_input=dict(block.input or {}),
                    outcome="shadow",
                    ok=True,
                    result_data=None,
                    error=None,
                    mode=mode,
                    iteration=iteration,
                )
                continue

            if vr.requires_approval:
                # Snapshot the tool_results we've already produced for
                # earlier blocks in THIS assistant turn. Without them
                # the resumed Anthropic call would violate the contract
                # "every tool_use must be paired with a tool_result in
                # the next user message" — Anthropic rejects partial
                # tool_result lists with 400 invalid_request_error.
                action_id = pending_actions.save(
                    ticket_id=str(
                        ticket.get("key") or ticket.get("ticket_id") or "?"
                    ),
                    playbook_id=playbook.id,
                    skill_name=block.name,
                    skill_input=dict(block.input or {}),
                    messages=messages,
                    tool_use_id=block.id,
                    iteration=iteration,
                    mode=mode,
                    partial_tool_results=list(tool_results),
                )
                return PlannerResult(
                    status="awaiting_approval",
                    pending_action_id=action_id,
                    iterations=iteration,
                )

            # Auto-execute (read in any mode, write under autonomous-opt-in)
            if skill is None:
                tool_results.append(
                    _tool_result_error(
                        block.id, f"skill {block.name} not registered"
                    )
                )
                continue
            skill_params = dict(block.input) if block.input else {}
            try:
                result = skill.execute(**skill_params)
            except Exception as exc:  # noqa: BLE001
                tool_results.append(
                    _tool_result_error(block.id, f"skill_crashed: {exc}")
                )
                _safe_audit(
                    ticket=ticket,
                    playbook_id=playbook.id,
                    skill_name=block.name,
                    skill_input=skill_params,
                    outcome="auto",
                    ok=False,
                    result_data=None,
                    error=f"skill_crashed: {exc}",
                    mode=mode,
                    iteration=iteration,
                )
                continue
            tool_results.append(_tool_result_from(block.id, result))
            _safe_audit(
                ticket=ticket,
                playbook_id=playbook.id,
                skill_name=block.name,
                skill_input=skill_params,
                outcome="auto",
                ok=result.ok,
                result_data=result.data if result.ok else None,
                error=result.error if not result.ok else None,
                mode=mode,
                iteration=iteration,
            )

        messages.append({"role": "user", "content": tool_results})

    return PlannerResult(
        status="max_iterations",
        error=f"hit {config.PLANNER_MAX_ITERATIONS} iterations without end_turn",
        iterations=iteration,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_client(client):
    if client is not None:
        return client
    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    from anthropic import Anthropic

    return Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _create_with_retry(client, **kwargs: Any):
    """Anthropic call with exponential backoff for 429/5xx.

    3 attempts max with 1s, 2s, 4s waits. 4xx (other than 429) fail-fast
    because they're not transient (auth, schema). 401/403 in particular
    must NOT retry — they signal a broken key, not a flaky service.
    """
    attempts = 3
    delays = [1.0, 2.0, 4.0]
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            return client.messages.create(**kwargs)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            status = _http_status_of(exc)
            transient = status is None or status == 429 or 500 <= status < 600
            if not transient or i == attempts - 1:
                raise
            wait = delays[min(i, len(delays) - 1)]
            log.warning(
                "anthropic call attempt %d/%d failed (status=%s); retrying in %.1fs",
                i + 1,
                attempts,
                status,
                wait,
            )
            time.sleep(wait)
    # unreachable — loop always returns or raises, but appease type checker
    assert last_exc is not None
    raise last_exc


def _http_status_of(exc: Exception) -> int | None:
    """Best-effort extraction of an HTTP status code from an Anthropic
    SDK exception. The SDK uses subclasses (RateLimitError, APIStatusError)
    that expose ``status_code``; older shapes attach ``response``."""
    code = getattr(exc, "status_code", None)
    if isinstance(code, int):
        return code
    resp = getattr(exc, "response", None)
    if resp is not None:
        code = getattr(resp, "status_code", None)
        if isinstance(code, int):
            return code
    return None


def _build_initial_prompt(
    ticket: dict[str, Any],
    playbook: Playbook,
) -> str:
    key = ticket.get("key") or ticket.get("ticket_id") or "(unknown)"
    summary = ticket.get("summary") or ""
    description = ticket.get("description") or "(no description)"
    parts = [
        "# Incoming ticket",
        f"Key: {key}",
        f"Summary: {summary}",
        "",
        "## Description",
        description,
        "",
        "# Matched playbook",
        f"Title: {playbook.title}",
        f"ID: {playbook.id}",
        "",
        playbook.body,
    ]
    parts.extend(
        [
            "",
            "# Task",
            "Use the available tools to advance this ticket per the playbook. "
            "Read context first if you need it. Stop when the resolution flow is complete.",
        ]
    )
    return "\n".join(parts)


def _content_block_to_dict(block) -> dict[str, Any]:
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
    return {"type": btype or "unknown"}


def _tool_result_from(tool_use_id: str, result) -> dict[str, Any]:
    if result.ok:
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": _compact(result.data),
        }
    return _tool_result_error(tool_use_id, f"error: {result.error}")


def _tool_result_error(tool_use_id: str, message: str) -> dict[str, Any]:
    return {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": message,
        "is_error": True,
    }


def _compact(data: Any) -> str:
    """Compact JSON-ish representation of skill output for Claude to read."""
    try:
        return json.dumps(data, ensure_ascii=False, default=str)
    except Exception:  # noqa: BLE001
        return str(data)


def _safe_audit(
    *,
    ticket: dict[str, Any],
    playbook_id: str,
    skill_name: str,
    skill_input: dict[str, Any],
    outcome: str,
    ok: bool,
    result_data: dict[str, Any] | None,
    error: str | None,
    mode: str,
    iteration: int,
) -> None:
    """Record an audit row, but never let an audit DB error kill the
    planner loop. SOC2 requires the audit; demo-grade safety requires
    that the agent keep working if the audit table is briefly locked."""
    try:
        agent_audit.record(
            ticket_id=str(ticket.get("key") or ticket.get("ticket_id") or "?"),
            playbook_id=playbook_id,
            skill_name=skill_name,
            skill_input=skill_input,
            outcome=outcome,
            ok=ok,
            result_data=result_data,
            error=error,
            mode=mode,
            iteration=iteration,
        )
    except Exception as exc:  # noqa: BLE001
        log.warning("audit record failed (%s): %s", skill_name, exc)


def _count_successful_writes(messages: list[dict[str, Any]]) -> int:
    """Walk the message history and count tool_result blocks that:

    1. are NOT is_error
    2. correspond to a previously-seen tool_use whose skill name is a
       registered write skill

    The pending_actions table doesn't track this — the source of truth
    is always the messages list itself. Failed writes (is_error=True)
    are excluded so the model can recover from a single transient error
    without immediately hitting the cap.
    """
    name_by_id: dict[str, str] = {}
    count = 0
    for msg in messages:
        role = msg.get("role")
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        if role == "assistant":
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tu_id = block.get("id")
                    name = block.get("name")
                    if tu_id and name:
                        name_by_id[tu_id] = name
        elif role == "user":
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "tool_result":
                    continue
                if block.get("is_error"):
                    continue
                tu_id = block.get("tool_use_id")
                if not tu_id:
                    continue
                name = name_by_id.get(tu_id)
                if not name:
                    continue
                skill_cls = REGISTRY.get(name)
                if skill_cls is None:
                    continue
                if skill_cls.is_write:
                    count += 1
    return count


def _last_text(content) -> str | None:
    for block in reversed(content):
        if getattr(block, "type", None) == "text":
            txt = getattr(block, "text", None)
            if txt:
                return txt
    return None


def _find_playbook(
    playbook_id: str,
    playbooks: Sequence[Playbook] | None,
) -> Playbook | None:
    if playbooks:
        for pb in playbooks:
            if pb.id == playbook_id:
                return pb
    # Fallback: glob the disk. Matches both ``id.md`` and ``id__hash.md``.
    matches = list(config.PLAYBOOKS_DIR.rglob(f"{playbook_id}.md"))
    if not matches:
        matches = list(config.PLAYBOOKS_DIR.rglob(f"{playbook_id}__*.md"))
    if not matches:
        return None
    return load_playbook(matches[0])
