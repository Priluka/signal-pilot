"""Agent loop — drives Claude tool_use to actually execute skills.

Two entrypoints:

- ``run(ticket, playbook, draft)`` → start a fresh planning session
- ``resume(action_id, approved, edited_input)`` → continue after HITL decision

The planner sits AFTER classify/retrieve/draft in ``core.agent_runner``. It
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
from dataclasses import dataclass
from typing import Any, Sequence

import config
from core import agent_config, pending_actions
from core.retrieval import Playbook, load_playbook
from core.skills.registry import get_skill, tools_for_playbook
from core.skills.validator import validate


_SYSTEM_PROMPT = """\
You are an agent helping a parking-company support team resolve a customer ticket.

You have been given:
- The ticket (summary, description, customer language signal)
- The matched playbook describing what to do for this type of problem
- The drafted reply for the customer (already prepared by the drafter)

Your job is to USE THE PROVIDED TOOLS to advance this ticket toward resolution:
- Read tools (get history, look up data) — call them first to verify context if useful
- Write tools (post a comment, change status) — call them to actually act

Rules:
- Only call tools that are in your tool list. Do not invent tool names.
- When the playbook's resolution flow is complete, end your turn with a brief plain-text summary of what you did.
- Do NOT call a tool if the playbook does not justify that action for this specific ticket.
- For public comments, write in the customer's language. Match the drafted reply unless the playbook says otherwise.
- Never ask the operator for permission in your text — the system handles approvals automatically based on tool risk.\
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
    draft_text: str | None = None,
    client=None,
) -> PlannerResult:
    """Start a fresh planner loop for one ticket."""
    mode = agent_config.effective_mode(playbook.id)
    tools = tools_for_playbook(playbook.metadata.get("allowed_skills") or [])
    if not tools:
        # Playbook has no skills wired up — planner is a no-op for it.
        return PlannerResult(status="done", iterations=0)

    messages: list[dict[str, Any]] = [
        {
            "role": "user",
            "content": _build_initial_prompt(ticket, playbook, draft_text),
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
        else:
            try:
                result = skill.execute(**params)
            except Exception as exc:  # noqa: BLE001
                tool_result = _tool_result_error(
                    pa.tool_use_id, f"skill_crashed: {exc}"
                )
            else:
                tool_result = _tool_result_from(pa.tool_use_id, result)
    else:
        tool_result = _tool_result_error(
            pa.tool_use_id,
            f"Operator rejected this action. "
            f"Reason: {rejection_note or 'no reason given'}. "
            "Try a different approach or end the turn.",
        )

    messages = list(pa.messages_blob)
    messages.append({"role": "user", "content": [tool_result]})

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
        iteration += 1
        try:
            response = client.messages.create(
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
                continue

            if vr.requires_approval:
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
            try:
                result = skill.execute(**(dict(block.input) if block.input else {}))
            except Exception as exc:  # noqa: BLE001
                tool_results.append(
                    _tool_result_error(block.id, f"skill_crashed: {exc}")
                )
                continue
            tool_results.append(_tool_result_from(block.id, result))

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


def _build_initial_prompt(
    ticket: dict[str, Any],
    playbook: Playbook,
    draft_text: str | None,
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
    if draft_text:
        parts.extend(["", "# Drafted reply (already written, for context)", draft_text])
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
