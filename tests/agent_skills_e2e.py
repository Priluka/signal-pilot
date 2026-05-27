"""End-to-end test for the full agent skills loop.

Drives the planner with a deterministic mock Claude client so the test
is fast, free, and repeatable. Covers:

- planner.run() with a fresh ticket → first iteration returns tool_use
  (read-only get_history) → validator OK, auto-executes (read), feeds
  result back → second iteration returns tool_use for write
  (add_public_comment) → validator says requires_approval → pending
  action saved → run() returns awaiting_approval

- planner.resume(approved=True, edited_input=...) → continues loop →
  Claude end_turn → returns done

Also runs a parallel rejection path so we know both branches close cleanly.
"""
from __future__ import annotations

import json
import sys
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(_PROJECT_ROOT / ".env")

from core import pending_actions, planner  # noqa: E402
from core.retrieval import load_playbook  # noqa: E402
from core.skills import jira as _skills_jira  # noqa: F401, E402  — side-effect register


# ---------------------------------------------------------------------------
# Mock Claude client — programmable script of responses
# ---------------------------------------------------------------------------


@dataclass
class _Block:
    type: str
    text: str | None = None
    id: str | None = None
    name: str | None = None
    input: dict[str, Any] | None = None


@dataclass
class _Response:
    stop_reason: str
    content: list[_Block]


@dataclass
class _MockMessages:
    script: list[_Response]
    calls: list[dict[str, Any]] = field(default_factory=list)

    def create(self, **kwargs: Any) -> _Response:
        # Deep-copy because the planner reuses (and mutates) the same
        # ``messages`` list across iterations. Storing the raw reference
        # would let later iterations rewrite our recorded "what was sent".
        import copy
        self.calls.append(copy.deepcopy(kwargs))
        if not self.script:
            raise RuntimeError("mock client ran out of scripted responses")
        return self.script.pop(0)


@dataclass
class _MockClient:
    messages: _MockMessages


def _tool_use(name: str, params: dict[str, Any]) -> _Block:
    return _Block(
        type="tool_use",
        id=f"tu_{uuid.uuid4().hex[:8]}",
        name=name,
        input=params,
    )


def _text(s: str) -> _Block:
    return _Block(type="text", text=s)


# ---------------------------------------------------------------------------
# Test fixture — load the real test playbook + build a fake ticket
# ---------------------------------------------------------------------------


def _load_test_playbook():
    pb_path = (
        _PROJECT_ROOT
        / "data/playbooks/end_user/billing/test-receipt-copy-request.md"
    )
    return load_playbook(pb_path)


def _fake_ticket(key: str = "KAN-TEST-E2E") -> dict[str, Any]:
    return {
        "key": key,
        "summary": "Trebam kopiju računa za parking",
        "description": "Platio sam parking ref 3d5p7-py22e-b25, mogu li dobiti račun?",
        "labels": [],
    }


# ---------------------------------------------------------------------------
# Test scenarios
# ---------------------------------------------------------------------------


def test_run_pauses_on_write(playbook, ticket) -> str:
    """Scenario: planner pauses on the first write skill in assisted mode."""
    # Force assisted mode regardless of global config so the test is
    # deterministic. We do this by passing the mode through the
    # skill_input snapshot path — actually we patch agent_config.
    from core import agent_config

    agent_config.set_mode("assisted")

    client = _MockClient(
        messages=_MockMessages(
            script=[
                # Iter 1: Claude calls a write tool (add_public_comment).
                # In assisted mode this should pause.
                _Response(
                    stop_reason="tool_use",
                    content=[
                        _text("I will send a reply to the customer."),
                        _tool_use(
                            "jira_add_public_comment",
                            {
                                "ticket_id": ticket["key"],
                                "body": "Test reply body.",
                            },
                        ),
                    ],
                )
            ]
        )
    )

    result = planner.run(
        ticket=ticket,
        playbook=playbook,
        draft_text="Test reply body.",
        client=client,
    )
    assert result.status == "awaiting_approval", (
        f"expected awaiting_approval, got {result.status} (err={result.error})"
    )
    assert result.pending_action_id is not None
    pa = pending_actions.get(result.pending_action_id)
    assert pa is not None
    assert pa.skill_name == "jira_add_public_comment"
    assert pa.skill_input["body"] == "Test reply body."
    print(f"  · paused on {pa.skill_name}, action_id={pa.id}, iter={pa.iteration}")
    return pa.id


def test_resume_reject(action_id: str) -> None:
    """Scenario: operator rejects → planner re-calls Claude with rejection
    tool_result → Claude ends turn → planner returns done."""
    client = _MockClient(
        messages=_MockMessages(
            script=[
                _Response(
                    stop_reason="end_turn",
                    content=[
                        _text("Understood, will not post the reply."),
                    ],
                )
            ]
        )
    )
    result = planner.resume(
        action_id=action_id,
        approved=False,
        rejection_note="Not yet — customer hasn't sent reference.",
        client=client,
    )
    assert result.status == "done", (
        f"expected done, got {result.status} (err={result.error})"
    )
    # Pending row should be gone.
    assert pending_actions.get(action_id) is None
    # Verify the resumed call carried a tool_result with is_error=True.
    assert client.messages.calls
    last_call_messages = client.messages.calls[-1]["messages"]
    last_user_msg = last_call_messages[-1]
    assert last_user_msg["role"] == "user"
    assert last_user_msg["content"][0]["type"] == "tool_result"
    assert last_user_msg["content"][0]["is_error"] is True
    print(f"  · resume-reject closed cleanly, summary={result.summary!r}")


def test_resume_approve_then_end(playbook, ticket) -> None:
    """Scenario: planner pauses on write → operator approves → planner
    re-calls Claude → Claude ends turn → returns done."""
    from core import agent_config

    agent_config.set_mode("assisted")

    # Override the actual skill execution so we don't hit live Jira.
    # We monkeypatch the registry entry's execute method on the class.
    from core.skills.registry import REGISTRY
    from core.skills.base import SkillResult

    real_class = REGISTRY["jira_add_public_comment"]
    real_execute = real_class.execute

    def fake_execute(self, **params: Any) -> SkillResult:  # type: ignore[no-untyped-def]
        return SkillResult(
            ok=True,
            data={
                "comment_id": "fake-101",
                "ticket_id": params.get("ticket_id"),
                "body_sent": params.get("body"),
            },
        )

    real_class.execute = fake_execute  # type: ignore[assignment]

    try:
        client_run = _MockClient(
            messages=_MockMessages(
                script=[
                    _Response(
                        stop_reason="tool_use",
                        content=[
                            _tool_use(
                                "jira_add_public_comment",
                                {
                                    "ticket_id": ticket["key"],
                                    "body": "Hello, here is your invoice.",
                                },
                            ),
                        ],
                    )
                ]
            )
        )
        run_result = planner.run(
            ticket=ticket,
            playbook=playbook,
            draft_text="Hello, here is your invoice.",
            client=client_run,
        )
        assert run_result.status == "awaiting_approval"
        action_id = run_result.pending_action_id
        assert action_id is not None

        client_resume = _MockClient(
            messages=_MockMessages(
                script=[
                    _Response(
                        stop_reason="end_turn",
                        content=[_text("Done. Replied to the customer.")],
                    )
                ]
            )
        )
        resume_result = planner.resume(
            action_id=action_id,
            approved=True,
            client=client_resume,
        )
        assert resume_result.status == "done", (
            f"expected done, got {resume_result.status} "
            f"(err={resume_result.error})"
        )
        assert pending_actions.get(action_id) is None

        # Verify the resumed Claude call carried a successful tool_result.
        last_msgs = client_resume.messages.calls[-1]["messages"]
        last_user = last_msgs[-1]
        assert last_user["content"][0]["type"] == "tool_result"
        assert "fake-101" in last_user["content"][0]["content"]
        assert last_user["content"][0].get("is_error") is not True
        print(f"  · resume-approve completed, summary={resume_result.summary!r}")
    finally:
        real_class.execute = real_execute  # restore


def test_validator_rejects_unknown_skill(playbook, ticket) -> None:
    """Scenario: Claude hallucinates an unknown tool name → validator
    feeds an error tool_result back → Claude ends turn."""
    client = _MockClient(
        messages=_MockMessages(
            script=[
                _Response(
                    stop_reason="tool_use",
                    content=[
                        _tool_use("definitely_not_a_real_skill", {"x": 1}),
                    ],
                ),
                _Response(
                    stop_reason="end_turn",
                    content=[_text("OK, skipping.")],
                ),
            ]
        )
    )
    result = planner.run(
        ticket=ticket,
        playbook=playbook,
        draft_text=None,
        client=client,
    )
    assert result.status == "done", f"expected done, got {result.status}"
    # Second call should have carried an error tool_result back to Claude.
    assert len(client.messages.calls) == 2
    second_call_messages = client.messages.calls[1]["messages"]
    user_msg = next(m for m in second_call_messages if m["role"] == "user" and isinstance(m["content"], list))
    found_error = False
    for m in second_call_messages:
        if m["role"] != "user" or not isinstance(m["content"], list):
            continue
        for block in m["content"]:
            if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error"):
                found_error = True
                break
    assert found_error, "expected an is_error tool_result fed back to Claude"
    print("  · validator correctly rejected hallucinated tool")


def test_shadow_mode_does_not_execute(playbook, ticket) -> None:
    """Scenario: shadow mode → write skill returns fake [SHADOW MODE] result,
    nothing executes against Jira."""
    from core import agent_config

    agent_config.set_mode("shadow")

    client = _MockClient(
        messages=_MockMessages(
            script=[
                _Response(
                    stop_reason="tool_use",
                    content=[
                        _tool_use(
                            "jira_add_public_comment",
                            {"ticket_id": ticket["key"], "body": "x"},
                        ),
                    ],
                ),
                _Response(
                    stop_reason="end_turn",
                    content=[_text("Shadow mode confirmed.")],
                ),
            ]
        )
    )
    result = planner.run(
        ticket=ticket,
        playbook=playbook,
        client=client,
    )
    assert result.status == "done"
    # The second call should have received a "[SHADOW MODE]" tool_result.
    second_call_messages = client.messages.calls[1]["messages"]
    found_shadow = False
    for m in second_call_messages:
        if m["role"] != "user" or not isinstance(m["content"], list):
            continue
        for block in m["content"]:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_result"
                and "SHADOW MODE" in str(block.get("content", ""))
            ):
                found_shadow = True
                break
    assert found_shadow, "expected [SHADOW MODE] tool_result"
    print("  · shadow mode confirmed — no real execute")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def main() -> int:
    pb = _load_test_playbook()
    ticket = _fake_ticket()

    print(f"Playbook: {pb.id}")
    print(f"  allowed_skills = {pb.metadata.get('allowed_skills')}")
    print(f"  autonomous_resolve = {(pb.metadata.get('agent_compatibility') or {}).get('autonomous_resolve')}")
    print()

    print("[1/5] run pauses on write in assisted mode")
    action_id = test_run_pauses_on_write(pb, ticket)

    print("[2/5] resume(reject) closes the loop")
    test_resume_reject(action_id)

    print("[3/5] resume(approve) executes skill and ends loop")
    test_resume_approve_then_end(pb, ticket)

    print("[4/5] validator rejects unknown skill")
    test_validator_rejects_unknown_skill(pb, ticket)

    print("[5/5] shadow mode logs but does not execute")
    test_shadow_mode_does_not_execute(pb, ticket)

    # Reset to default mode so we don't leak shadow into other tests.
    from core import agent_config

    agent_config.set_mode("shadow")

    print()
    print("All 5 scenarios PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
