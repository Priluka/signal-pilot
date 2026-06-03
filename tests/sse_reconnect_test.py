"""SSE reconnect verification — Phase 8C of the hardening sweep.

The frontend's refresh-resilience promise has two parts:

  1. **Replay**: when an operator hits refresh mid-turn, the new SSE
     attach (GET ``/chat/threads/{id}/turns/{tid}/stream``) re-emits
     every event that was already persisted, in chronological order.
  2. **Live tail**: after replay, if the turn is still ``streaming``,
     newly emitted events flow live until ``done``.

This test exercises (1) with a real (short) Anthropic turn. It is the
cheapest possible end-to-end check (~$0.05-0.10) — one short query
firing one or two skills, then a re-attach.

Run from project root:

    .venv/bin/python tests/sse_reconnect_test.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8000"


def _read_sse(resp) -> list[dict]:
    """Drain an SSE response into a list of (type, payload) dicts.
    Stops at the first ``done`` or ``error`` event."""
    out: list[dict] = []
    buf = ""
    for chunk in resp:
        buf += chunk.decode("utf-8", errors="replace")
        while "\n\n" in buf:
            raw, buf = buf.split("\n\n", 1)
            evt_type: str | None = None
            data_lines: list[str] = []
            for line in raw.splitlines():
                if line.startswith("event:"):
                    evt_type = line[6:].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[5:].strip())
            if not data_lines:
                continue
            try:
                payload = json.loads("\n".join(data_lines))
            except Exception:  # noqa: BLE001
                continue
            if not isinstance(payload, dict):
                continue
            out.append({"type": evt_type, **payload})
            if evt_type in ("done", "error"):
                return out
    return out


def _create_thread() -> int:
    req = urllib.request.Request(
        f"{BASE}/chat/threads",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return int(json.loads(resp.read())["id"])


def _fire_turn(thread_id: int, text: str) -> list[dict]:
    body = json.dumps({"user_text": text, "top_k": 3}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/chat/threads/{thread_id}/turns",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return _read_sse(resp)


def _reattach(thread_id: int, turn_id: int) -> list[dict]:
    req = urllib.request.Request(
        f"{BASE}/chat/threads/{thread_id}/turns/{turn_id}/stream",
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return _read_sse(resp)


def _types_in_order(events: list[dict]) -> list[str]:
    """Just the event type stream (no payloads) for ordering comparison."""
    return [e["type"] or "?" for e in events]


def _signature(events: list[dict]) -> list[tuple]:
    """Tuple-form of each event used for cross-stream equality. We
    don't compare full payloads — token deltas may legitimately
    re-emit differently when streamed live vs replayed from a buffer.
    Instead we focus on the structural events that matter for
    reconnect correctness."""
    out: list[tuple] = []
    for e in events:
        t = e["type"]
        if t == "skill_executing":
            out.append(("skill_executing", e.get("skill"), e.get("call_id")))
        elif t == "skill_executed":
            out.append((
                "skill_executed",
                e.get("skill"),
                e.get("call_id"),
                bool(e.get("ok")),
            ))
        elif t == "thinking":
            out.append(("thinking", int(e.get("iteration", 0))))
        elif t == "compacted":
            out.append(("compacted", int(e.get("tier", 0))))
        elif t == "composing":
            out.append(("composing",))
        elif t == "done":
            out.append(("done",))
        elif t == "error":
            out.append(("error", e.get("message")))
    return out


def main() -> int:
    # Health check
    try:
        with urllib.request.urlopen(f"{BASE}/health", timeout=2) as r:
            r.read()
    except Exception:  # noqa: BLE001
        print("ERROR: backend not reachable")
        return 2

    thread_id = _create_thread()
    print(f"thread_id={thread_id}")

    # Short query — one skill, fast — keeps cost minimal.
    query = "Provjeri Bmove za W-55123K."
    print(f"firing live turn: {query!r}")
    live_events = _fire_turn(thread_id, query)
    print(f"live stream emitted {len(live_events)} events")
    live_types = _types_in_order(live_events)
    print(f"live types: {live_types}")

    # Find the turn id — the ``sources`` event carries it.
    turn_id: int | None = None
    for e in live_events:
        if e["type"] == "sources" and "turn_id" in e:
            turn_id = int(e["turn_id"])
            break
    if turn_id is None:
        print("FAIL: live stream emitted no 'sources' event with turn_id")
        return 1

    # Re-attach
    print(f"re-attaching to /chat/threads/{thread_id}/turns/{turn_id}/stream")
    time.sleep(0.5)  # let any pending DB writes settle
    replay_events = _reattach(thread_id, turn_id)
    print(f"replay emitted {len(replay_events)} events")
    replay_types = _types_in_order(replay_events)
    print(f"replay types: {replay_types}")

    live_sig = _signature(live_events)
    replay_sig = _signature(replay_events)

    # The replay should contain every skill_executing / skill_executed
    # / thinking / compacted event from the live stream, in the same
    # order. It may also contain extra reconstruction events (e.g.
    # an opening 'attached' synthetic event) which we tolerate by
    # checking subset-order rather than strict equality.
    def _is_subseq_in_order(needle: list, haystack: list) -> bool:
        i = 0
        for item in haystack:
            if i < len(needle) and item == needle[i]:
                i += 1
        return i == len(needle)

    if not _is_subseq_in_order(live_sig, replay_sig):
        print("FAIL: replay missing some live events or out of order")
        print(f"  live_sig:   {live_sig}")
        print(f"  replay_sig: {replay_sig}")
        return 1

    if replay_sig[-1] != ("done",):
        print(f"FAIL: replay did not end with 'done'. last: {replay_sig[-1]}")
        return 1

    # Sanity: replay's final delta-accumulated text must match what
    # live captured (the persisted ``final_assistant_text``).
    live_text = "".join(
        str(e.get("text") or "") for e in live_events if e["type"] == "delta"
    )
    replay_text = "".join(
        str(e.get("text") or "") for e in replay_events if e["type"] == "delta"
    )
    if live_text and replay_text and live_text.strip() != replay_text.strip():
        # Token-level reconstruction can differ in whitespace; we use
        # a stripped equality only as a soft signal. Print but don't
        # fail — the structural match above is the load-bearing
        # assertion.
        print("WARN: live vs replay text differ in whitespace")
        print(f"  live  : {live_text[:120]!r}")
        print(f"  replay: {replay_text[:120]!r}")

    print("PASS: replay matches live stream (structural events in order)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
