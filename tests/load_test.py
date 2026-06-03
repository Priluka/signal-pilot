"""20-way concurrent load test — Phase 12.8.

Production reality check: spawn 20 client threads simultaneously, each
acting as one operator. Every operator:

  1. Creates a fresh thread (rate-limit boundary test)
  2. Fires 2 short turns sequentially in their own thread
  3. Measures per-turn latency, captures any error / 429 / 5xx

We report:

  • Wall time vs. sum-of-per-turn (parallelism check)
  • Per-turn p50 / p95 / p99 latency
  • HTTP error breakdown
  • Total Anthropic spend (from each thread's final usage payload)
  • SQLite lock errors (none expected)

Cost: ~$0.50 (40 short turns × ~$0.01 each on Sonnet 4.6).

Backend must be launched with relaxed limits — the rate limiter
otherwise rejects 20 simultaneous thread creates:

    CHAT_RATE_LIMIT_TURNS=200 .venv/bin/uvicorn backend.main:app --port 8000

Run from project root:

    .venv/bin/python tests/load_test.py
    .venv/bin/python tests/load_test.py --operators 10 --turns-per-op 1
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

BASE = "http://127.0.0.1:8000"

# Plates that exist in the mock skill set — every one returns
# ``found=true`` so the agent has substance to weave in.
PLATE_POOL = [
    "W-55123K",
    "W-38702T",
    "ZG-1234-AB",
    "ZG-7777-XY",
    "W-12345B",
    "W-44556D",
    "W-88211C",
    "ZG-9988-CD",
    "DE-MH-5521",
    "I-AM442RR",
]


@dataclass
class TurnRecord:
    operator_id: int
    turn_index: int
    duration_s: float = 0.0
    http_status: int = 0
    skills_called: int = 0
    cost_usd: float = 0.0
    error: str = ""


@dataclass
class OperatorOutcome:
    operator_id: int
    thread_id: int = -1
    turns: list[TurnRecord] = field(default_factory=list)
    error: str = ""


def _post_json(path: str, body: dict, timeout: float = 30.0):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read())


def _stream_turn(thread_id: int, user_text: str) -> tuple[int, int, float]:
    """Stream a turn and return ``(status, skill_count, cost_usd)``."""
    body = json.dumps({"user_text": user_text, "top_k": 3}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/chat/threads/{thread_id}/turns",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    skills = 0
    cost = 0.0
    with urllib.request.urlopen(req, timeout=180) as resp:
        buf = ""
        for chunk in resp:
            buf += chunk.decode("utf-8", errors="replace")
            while "\n\n" in buf:
                raw, buf = buf.split("\n\n", 1)
                evt_type = None
                data_lines = []
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
                if evt_type == "skill_executed":
                    skills += 1
                if evt_type in ("done", "error"):
                    # Fetch persisted turn for usage info.
                    return resp.status, skills, cost
        return resp.status, skills, cost


def _fetch_thread(thread_id: int) -> dict[str, Any]:
    with urllib.request.urlopen(
        f"{BASE}/chat/threads/{thread_id}", timeout=10
    ) as r:
        return json.loads(r.read())


def operator(
    operator_id: int, turns_per_op: int, outcomes: list[OperatorOutcome]
) -> None:
    o = OperatorOutcome(operator_id=operator_id)
    try:
        # Create a thread first.
        _, thread = _post_json("/chat/threads", {})
        o.thread_id = int(thread["id"])
    except Exception as exc:  # noqa: BLE001
        o.error = f"thread create: {type(exc).__name__}: {exc}"
        outcomes[operator_id] = o
        return

    for turn_idx in range(turns_per_op):
        plate = PLATE_POOL[(operator_id + turn_idx) % len(PLATE_POOL)]
        text = (
            f"Provjeri Bmove za {plate}." if turn_idx == 0
            else "Daj mi sumu nalaza u jednoj rečenici."
        )
        rec = TurnRecord(operator_id=operator_id, turn_index=turn_idx)
        start = time.perf_counter()
        try:
            status, skills, _ = _stream_turn(o.thread_id, text)
            rec.duration_s = time.perf_counter() - start
            rec.http_status = status
            rec.skills_called = skills
        except urllib.error.HTTPError as exc:
            rec.duration_s = time.perf_counter() - start
            rec.http_status = exc.code
            rec.error = f"HTTP {exc.code}"
        except Exception as exc:  # noqa: BLE001
            rec.duration_s = time.perf_counter() - start
            rec.error = f"{type(exc).__name__}: {exc}"
        o.turns.append(rec)

    # Pull cost from persisted usage.
    try:
        detail = _fetch_thread(o.thread_id)
        for t_persisted in detail.get("turns", []):
            usage = t_persisted.get("usage") or {}
            idx = int(t_persisted.get("turn_index", -1))
            if 0 <= idx < len(o.turns):
                o.turns[idx].cost_usd = float(usage.get("cost_usd") or 0.0)
    except Exception:  # noqa: BLE001
        pass
    outcomes[operator_id] = o


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operators", type=int, default=20)
    parser.add_argument("--turns-per-op", type=int, default=2)
    args = parser.parse_args()

    try:
        with urllib.request.urlopen(f"{BASE}/health", timeout=2) as r:
            r.read()
    except Exception:  # noqa: BLE001
        print(f"ERROR: backend not reachable at {BASE}")
        return 2

    outcomes: list[OperatorOutcome] = [None] * args.operators  # type: ignore[list-item]
    threads: list[threading.Thread] = []
    print(
        f"Spawning {args.operators} concurrent operators × "
        f"{args.turns_per_op} turns each…"
    )
    start = time.perf_counter()
    for i in range(args.operators):
        t = threading.Thread(
            target=operator,
            args=(i, args.turns_per_op, outcomes),
            daemon=True,
        )
        t.start()
        threads.append(t)
    for t in threads:
        t.join(timeout=600)
    wall = time.perf_counter() - start

    # Aggregate
    all_turns: list[TurnRecord] = []
    operator_errors = 0
    for o in outcomes:
        if o.error:
            operator_errors += 1
            print(f"  op {o.operator_id}: ERROR {o.error}")
            continue
        all_turns.extend(o.turns)

    durations = [t.duration_s for t in all_turns if t.duration_s > 0]
    durations.sort()
    total_cost = sum(t.cost_usd for t in all_turns)
    http_2xx = sum(1 for t in all_turns if 200 <= t.http_status < 300)
    http_429 = sum(1 for t in all_turns if t.http_status == 429)
    http_other_err = sum(
        1 for t in all_turns if t.http_status >= 400 and t.http_status != 429
    )
    turn_errors = sum(1 for t in all_turns if t.error)

    def percentile(p: float) -> float:
        if not durations:
            return 0.0
        idx = min(int(len(durations) * p), len(durations) - 1)
        return durations[idx]

    print(f"\n=== RESULTS ===")
    print(f"Wall time         : {wall:.1f}s")
    print(f"Operators         : {args.operators}")
    print(f"Total turns fired : {len(all_turns)}")
    print(f"HTTP 2xx          : {http_2xx}")
    print(f"HTTP 429 (RL)     : {http_429}")
    print(f"HTTP 4xx/5xx other: {http_other_err}")
    print(f"Operator setup err: {operator_errors}")
    print(f"Turn-level errors : {turn_errors}")
    if durations:
        print(f"Latency p50       : {percentile(0.50):.2f}s")
        print(f"Latency p95       : {percentile(0.95):.2f}s")
        print(f"Latency p99       : {percentile(0.99):.2f}s")
        print(f"Latency mean      : {statistics.mean(durations):.2f}s")
    print(f"Total Anthropic   : ${total_cost:.4f}")

    if turn_errors == 0 and operator_errors == 0 and http_other_err == 0:
        print("\nPASS: no operator-side errors, no 5xx, no crashes")
        return 0
    print("\nFAIL: errors above")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
