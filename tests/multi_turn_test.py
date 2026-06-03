"""Multi-turn chat coverage — Phase 6 of the Claude-Code-level rebuild.

Four buckets:

  6a. Context carry — turn N's agent sees tool_results from turns 1..N-1.
  6b. Compaction triggers — Tier 1 (snip) and Tier 2 (drop) emit a
       ``compacted`` event the UI can render.
  6c. Refresh-during-stream — the SSE tail replays already-persisted
       events before resuming the live stream.
  6d. FK cascade — deleting a thread removes all of its chat_turns rows.

Most tests run in-process (no backend needed). 6a is the only test that
actually calls Anthropic; everything else uses the pure persistence /
compaction layer with synthetic data.

Run from project root:

    .venv/bin/python tests/multi_turn_test.py
    .venv/bin/python tests/multi_turn_test.py --skip-llm   # skip 6a only
    .venv/bin/python tests/multi_turn_test.py --names cascade
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from core import chat_agent, chat_threads  # noqa: E402
from core.chat_agent import (  # noqa: E402
    _COMPACT_KEEP_LAST_N_TURNS,
    _compact_messages,
)


# ---------------------------------------------------------------------------
# Runner scaffold
# ---------------------------------------------------------------------------


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_s: float
    detail: str = ""
    error: str = ""


@dataclass
class Suite:
    results: list[TestResult] = field(default_factory=list)

    def run(self, name: str, fn: Callable[[], str]) -> None:
        print(f"\n=== {name} ===")
        start = time.perf_counter()
        try:
            detail = fn()
            self.results.append(
                TestResult(
                    name=name,
                    passed=True,
                    duration_s=time.perf_counter() - start,
                    detail=detail,
                )
            )
            print(f"  PASS ({time.perf_counter() - start:.2f}s) — {detail}")
        except AssertionError as exc:
            self.results.append(
                TestResult(
                    name=name,
                    passed=False,
                    duration_s=time.perf_counter() - start,
                    error=str(exc),
                )
            )
            print(f"  FAIL — {exc}")
        except Exception as exc:  # noqa: BLE001
            self.results.append(
                TestResult(
                    name=name,
                    passed=False,
                    duration_s=time.perf_counter() - start,
                    error=f"{type(exc).__name__}: {exc}",
                )
            )
            print(f"  ERROR — {type(exc).__name__}: {exc}")

    def summary(self) -> int:
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print(f"\n{'=' * 60}")
        print(f"Multi-turn suite: {passed}/{total} passed")
        for r in self.results:
            mark = "✓" if r.passed else "✗"
            tail = r.detail if r.passed else r.error
            print(f"  {mark} {r.name} ({r.duration_s:.2f}s) — {tail}")
        return 0 if passed == total else 1


# ---------------------------------------------------------------------------
# 6a — context carry (LLM-backed, single multi-turn convo)
# ---------------------------------------------------------------------------


_BACKEND_BASE = "http://127.0.0.1:8000"


def _backend_reachable() -> bool:
    """Probe the running backend. Backend is responsible for loading
    ANTHROPIC_API_KEY from .env — the test only needs HTTP access."""
    import urllib.request

    try:
        with urllib.request.urlopen(
            f"{_BACKEND_BASE}/health", timeout=2.0
        ) as resp:
            return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


def _stream_turn(thread_id: int, user_text: str) -> tuple[int, list[dict[str, Any]], str]:
    """POST to /chat/threads/{id}/turns, parse SSE, return
    (turn_id, all_events, final_text). Blocks until the stream
    emits ``done`` or ``error``."""
    import urllib.request

    body = json.dumps({"user_text": user_text, "top_k": 3}).encode("utf-8")
    req = urllib.request.Request(
        f"{_BACKEND_BASE}/chat/threads/{thread_id}/turns",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    events: list[dict[str, Any]] = []
    turn_id = -1
    final_text = ""
    with urllib.request.urlopen(req, timeout=180) as resp:
        buf = ""
        for chunk in resp:
            buf += chunk.decode("utf-8", errors="replace")
            while "\n\n" in buf:
                raw_evt, buf = buf.split("\n\n", 1)
                evt_type: str | None = None
                data_lines: list[str] = []
                for line in raw_evt.splitlines():
                    if line.startswith("event:"):
                        evt_type = line[6:].strip()
                    elif line.startswith("data:"):
                        data_lines.append(line[5:].strip())
                if not data_lines:
                    continue
                payload_raw = "\n".join(data_lines)
                try:
                    payload = json.loads(payload_raw)
                except Exception:  # noqa: BLE001
                    continue
                if not isinstance(payload, dict):
                    continue
                evt = {"type": evt_type, **payload}
                events.append(evt)
                if evt_type == "turn":
                    turn_id = int(payload["turn"]["id"])
                if evt_type == "delta":
                    final_text += str(payload.get("text") or "")
                if evt_type in ("done", "error"):
                    return turn_id, events, final_text
    return turn_id, events, final_text


def test_context_carry() -> str:
    """Two-turn dialogue where turn 2 references turn 1's tool calls.

    Turn 1: ``Provjeri Bmove za HR1234AB.``  → bmove_user_lookup fires.
    Turn 2: ``A je li ima neku Datatrans transakciju?`` → no plate in
              the text. If context carries, the agent picks HR1234AB
              from turn 1 and calls datatrans_transaction with it.
    """
    import urllib.request

    if not _backend_reachable():
        raise AssertionError(
            f"Backend not reachable at {_BACKEND_BASE} — start it first"
        )

    # Create empty thread via API
    req = urllib.request.Request(
        f"{_BACKEND_BASE}/chat/threads",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        thread = json.loads(resp.read().decode("utf-8"))
    thread_id = int(thread["id"])

    # Turn 1
    turn_id_1, events_1, text_1 = _stream_turn(
        thread_id, "Provjeri Bmove za HR1234AB."
    )
    skill_events_1 = [
        e for e in events_1
        if e.get("type") in ("skill_executing", "skill_executed")
    ]
    assert skill_events_1, (
        f"turn 1 fired no skills. events: {[e.get('type') for e in events_1[:10]]}"
    )
    print(f"  turn 1 fired {len(skill_events_1)} skill events")

    # Turn 2 — no plate in text. Context must carry HR1234AB.
    turn_id_2, events_2, text_2 = _stream_turn(
        thread_id, "A je li ima neku Datatrans transakciju za tu plate?"
    )
    print(f"  turn 2 answer head: {text_2[:200]!r}")

    plate_in_skill_params = False
    for ev in events_2:
        if ev.get("type") in ("skill_executing", "skill_executed"):
            params = ev.get("params", {}) or {}
            blob = json.dumps(params).upper()
            if "HR1234AB" in blob:
                plate_in_skill_params = True
                break
    plate_in_text = "HR1234AB" in text_2.upper()
    assert plate_in_skill_params or plate_in_text, (
        f"turn 2 did not carry HR1234AB from turn 1. "
        f"answer_head={text_2[:200]!r}"
    )
    return (
        f"thread={thread_id} t1_turn={turn_id_1} t2_turn={turn_id_2} "
        f"plate_in_skill={plate_in_skill_params} plate_in_text={plate_in_text}"
    )


# ---------------------------------------------------------------------------
# 6b — compaction events (Tier 1 and Tier 2)
# ---------------------------------------------------------------------------


def _fake_tool_result_message(call_id: str, payload_len: int) -> dict[str, Any]:
    """Synthesise a user message holding a single tool_result block big
    enough to drive token counts above the snip threshold."""
    payload = "x" * payload_len
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": call_id,
                "content": payload,
            }
        ],
    }


def _fake_tool_use_message(call_id: str) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": call_id,
                "name": "bmove_user_lookup",
                "input": {"plate": "HR0000AA"},
            }
        ],
    }


def _fake_user_text(text: str) -> dict[str, Any]:
    return {"role": "user", "content": text}


def _fake_assistant_text(text: str) -> dict[str, Any]:
    return {
        "role": "assistant",
        "content": [{"type": "text", "text": text}],
    }


def _build_synthetic_history(num_turns: int, big_tool_chars: int) -> list[dict[str, Any]]:
    """Each turn = user msg + tool_use + tool_result + assistant text.
    Tunable via num_turns + big_tool_chars."""
    msgs: list[dict[str, Any]] = []
    for i in range(num_turns):
        msgs.append(_fake_user_text(f"Korisnik turn {i}: opis problema."))
        msgs.append(_fake_tool_use_message(f"call_{i}"))
        msgs.append(_fake_tool_result_message(f"call_{i}", big_tool_chars))
        msgs.append(
            _fake_assistant_text(
                f"Agent sažima rezultat za turn {i}, vrlo kratko: ok."
            )
        )
    return msgs


class _PatchedThreshold:
    """Context manager that swaps ``_COMPACT_THRESHOLD_TOKENS`` to a
    test-friendly value. Real default (160k) requires huge fixtures
    that slow the test loop and obscure the assertion."""

    def __init__(self, value: int) -> None:
        self._value = value
        self._original: int | None = None

    def __enter__(self) -> "_PatchedThreshold":
        self._original = chat_agent._COMPACT_THRESHOLD_TOKENS
        chat_agent._COMPACT_THRESHOLD_TOKENS = self._value
        return self

    def __exit__(self, *exc: Any) -> None:
        chat_agent._COMPACT_THRESHOLD_TOKENS = self._original  # type: ignore[assignment]


def test_compaction_tier1_emits() -> str:
    """Force a tier-1 (snip) compaction by lowering the threshold so
    a small synthetic history goes over budget. After snipping the old
    tool_results to 400 chars each, we should land below the threshold
    and the pipeline must emit a ``compacted`` event."""
    msgs = _build_synthetic_history(num_turns=6, big_tool_chars=4_000)
    captured: list[dict[str, Any]] = []

    def on_event(kind: str, payload: dict[str, Any]) -> None:
        captured.append({"type": kind, **payload})

    # Pick threshold between snipped and un-snipped sizes so tier 1
    # alone is enough. 6 turns × 4k chars of tool_result ≈ 24k chars
    # ≈ 6k tokens; snipping to 400 chars × 4 old turns ≈ 1.6k chars
    # ≈ 400 tokens. Threshold 2_500 sits between.
    with _PatchedThreshold(2_500):
        new_msgs, info = _compact_messages(
            msgs, client=None, on_event=on_event
        )

    assert info["tier"] >= 1, f"expected tier>=1, got {info}"
    compacted_events = [e for e in captured if e["type"] == "compacted"]
    assert compacted_events, f"no compacted event emitted. info={info}"
    ev = compacted_events[0]
    assert ev["tier"] in (1, 2), f"expected tier 1 or 2, got {ev}"
    assert ev["before_tokens"] == info["before_tokens"]
    assert ev["after_tokens"] == info["after_tokens"]
    assert ev["after_tokens"] < ev["before_tokens"]
    return (
        f"tier={ev['tier']} before={ev['before_tokens']} "
        f"after={ev['after_tokens']} kept={len(new_msgs)} msgs"
    )


def test_compaction_tier2_drops_turns() -> str:
    """Force a tier-2 (drop oldest) compaction by setting the threshold
    so tight that snipping alone (which still keeps the recent
    un-snipped tool_results) can't bring tokens below budget — the
    pipeline must escalate to dropping old turns wholesale."""
    msgs = _build_synthetic_history(num_turns=8, big_tool_chars=10_000)
    captured: list[dict[str, Any]] = []

    def on_event(kind: str, payload: dict[str, Any]) -> None:
        captured.append({"type": kind, **payload})

    # Recent 2 turns each carry ~10k char tool_results = ~2.5k tokens
    # each = ~5k tokens for the keep-window alone. Threshold below
    # that forces tier 2 to drop old turns until under budget.
    with _PatchedThreshold(4_000):
        new_msgs, info = _compact_messages(
            msgs, client=None, on_event=on_event
        )

    assert info["tier"] == 2, (
        f"expected tier=2 (snip wasn't enough), got info={info}"
    )
    assert info["dropped_turns"] >= 1, f"no turns dropped: {info}"
    compacted_events = [e for e in captured if e["type"] == "compacted"]
    assert compacted_events, f"no compacted event emitted. info={info}"
    ev = compacted_events[-1]
    assert ev["tier"] == 2
    assert ev["dropped_turns"] >= 1
    # The keep-floor invariant: at least the last N turns survive (each
    # turn = 4 messages in our fixture).
    assert len(new_msgs) >= _COMPACT_KEEP_LAST_N_TURNS * 4 - 1, (
        f"kept too few messages: {len(new_msgs)}"
    )
    return (
        f"tier={ev['tier']} dropped={ev['dropped_turns']} "
        f"before={ev['before_tokens']} after={ev['after_tokens']}"
    )


def test_compaction_below_threshold_noop() -> str:
    """Short history must NOT compact and must NOT emit the event."""
    msgs = _build_synthetic_history(num_turns=2, big_tool_chars=200)
    captured: list[dict[str, Any]] = []

    def on_event(kind: str, payload: dict[str, Any]) -> None:
        captured.append({"type": kind, **payload})

    new_msgs, info = _compact_messages(msgs, client=None, on_event=on_event)
    assert info["tier"] == 0, f"expected no-op, got {info}"
    assert new_msgs == msgs, "no-op compaction must return identity"
    assert not any(e["type"] == "compacted" for e in captured), (
        f"unexpected compacted event for under-threshold history: {captured}"
    )
    return f"before={info['before_tokens']} after={info['after_tokens']} tier=0"


# ---------------------------------------------------------------------------
# 6c — refresh during stream (events_json replay)
# ---------------------------------------------------------------------------


def test_events_persist_in_order() -> str:
    """Persistence of events as the agent runs is what enables refresh
    resilience: the SSE tail replays whatever ``events_json`` already
    has, then continues live. We verify that the persistence callback
    actually writes events in chronological order."""
    thread = chat_threads.create_thread(title="events-order test")
    turn = chat_threads.create_pending_turn(
        thread_id=thread.id, user_text="dummy"
    )

    bucket: list[dict[str, Any]] = []
    for i in range(20):
        kind = "skill_executing" if i % 2 == 0 else "skill_executed"
        bucket.append({"type": kind, "seq": i, "call_id": f"c{i // 2}"})
        chat_threads.update_turn(turn.id, events=bucket)

    reloaded = chat_threads.get_turn(turn.id)
    assert reloaded is not None
    assert reloaded.events is not None
    seqs = [e.get("seq") for e in reloaded.events]
    assert seqs == list(range(20)), f"events out of order: {seqs}"
    return f"persisted {len(seqs)} events in order"


# ---------------------------------------------------------------------------
# 6d — FK cascade
# ---------------------------------------------------------------------------


def test_thread_delete_cascade() -> str:
    """Create thread, add 2 turns with events, delete thread,
    assert no orphan chat_turns rows remain for that thread_id."""
    thread = chat_threads.create_thread(title="cascade test")
    t1 = chat_threads.create_pending_turn(
        thread_id=thread.id, user_text="turn 1"
    )
    chat_threads.update_turn(
        t1.id, events=[{"type": "skill_executing", "skill": "x"}]
    )
    t2 = chat_threads.create_pending_turn(
        thread_id=thread.id, user_text="turn 2"
    )
    chat_threads.update_turn(t2.id, final_assistant_text="ok", status="done")

    pre = chat_threads.list_turns_for_thread(thread.id)
    assert len(pre) == 2, f"expected 2 turns, got {len(pre)}"

    deleted = chat_threads.delete_thread(thread.id)
    assert deleted, "delete returned False"

    post = chat_threads.list_turns_for_thread(thread.id)
    assert post == [], f"FK cascade did not remove children: {post}"

    assert chat_threads.get_thread(thread.id) is None
    return f"thread={thread.id} cascade removed 2 turns"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


ALL_TESTS: dict[str, Callable[[], str]] = {
    "context-carry": test_context_carry,
    "compaction-tier1": test_compaction_tier1_emits,
    "compaction-tier2": test_compaction_tier2_drops_turns,
    "compaction-noop": test_compaction_below_threshold_noop,
    "events-order": test_events_persist_in_order,
    "cascade": test_thread_delete_cascade,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip Anthropic-backed tests (context-carry only)",
    )
    parser.add_argument(
        "--names",
        nargs="*",
        default=None,
        help="Run only the named tests",
    )
    args = parser.parse_args()

    suite = Suite()
    for name, fn in ALL_TESTS.items():
        if args.names is not None and name not in args.names:
            continue
        if args.skip_llm and name == "context-carry":
            print(f"\n=== {name} ===\n  SKIP (--skip-llm)")
            continue
        suite.run(name, fn)
    return suite.summary()


if __name__ == "__main__":
    raise SystemExit(main())
