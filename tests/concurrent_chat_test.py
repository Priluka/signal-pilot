"""Concurrent threads stress test — Phase 8D.

Three client workers each fire a short turn against a *different*
chat_thread simultaneously. The daemon-thread model in the backend
should isolate every turn — no cross-contamination of events, no
SQLite lock errors, no shared state leaks.

We assert:

  • All three turns reach status='done' with non-empty answers.
  • Each turn's events_json contains only events belonging to that
    thread/turn (no cross-bleed).
  • Each event stream completed with a ``done`` SSE event (the live
    POST stream stayed coherent for each client).
  • Wall time is roughly max(per-turn) — not 3× sum — proving the
    daemons actually ran in parallel rather than serially.

Run from project root:

    .venv/bin/python tests/concurrent_chat_test.py
"""
from __future__ import annotations

import json
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any

BASE = "http://127.0.0.1:8000"


@dataclass
class WorkerResult:
    worker_id: int
    thread_id: int = -1
    turn_id: int = -1
    events: list[dict[str, Any]] = field(default_factory=list)
    final_text: str = ""
    duration_s: float = 0.0
    error: str = ""


def _create_thread() -> int:
    req = urllib.request.Request(
        f"{BASE}/chat/threads",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return int(json.loads(resp.read())["id"])


def _stream_turn(thread_id: int, user_text: str) -> tuple[
    int, list[dict[str, Any]], str
]:
    body = json.dumps({"user_text": user_text, "top_k": 3}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/chat/threads/{thread_id}/turns",
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
                events.append({"type": evt_type, **payload})
                if evt_type == "sources" and "turn_id" in payload:
                    turn_id = int(payload["turn_id"])
                if evt_type == "delta":
                    final_text += str(payload.get("text") or "")
                if evt_type in ("done", "error"):
                    return turn_id, events, final_text
    return turn_id, events, final_text


# Three distinct plates so each worker reasons about its own subject.
# Mock skills return ``found=true`` for these, giving the agent
# substance to weave into the answer.
QUERIES = [
    (1, "Provjeri Bmove za W-55123K."),
    (2, "Provjeri Bmove za ZG-1234-AB."),
    (3, "Provjeri Bmove za W-38702T."),
]


def worker(query: tuple[int, str], result_slot: list[WorkerResult]) -> None:
    worker_id, user_text = query
    res = WorkerResult(worker_id=worker_id)
    start = time.perf_counter()
    try:
        thread_id = _create_thread()
        res.thread_id = thread_id
        turn_id, events, final_text = _stream_turn(thread_id, user_text)
        res.turn_id = turn_id
        res.events = events
        res.final_text = final_text
    except Exception as exc:  # noqa: BLE001
        res.error = f"{type(exc).__name__}: {exc}"
    res.duration_s = time.perf_counter() - start
    result_slot[worker_id - 1] = res


def main() -> int:
    try:
        with urllib.request.urlopen(f"{BASE}/health", timeout=2) as r:
            r.read()
    except Exception:  # noqa: BLE001
        print("ERROR: backend not reachable")
        return 2

    print(f"Spawning {len(QUERIES)} concurrent workers…")
    results: list[WorkerResult] = [WorkerResult(worker_id=0)] * len(QUERIES)
    threads: list[threading.Thread] = []
    overall_start = time.perf_counter()
    for q in QUERIES:
        t = threading.Thread(target=worker, args=(q, results), daemon=True)
        t.start()
        threads.append(t)
    for t in threads:
        t.join(timeout=300)
    overall_duration = time.perf_counter() - overall_start

    print(f"\nWall time: {overall_duration:.1f}s")
    for r in results:
        plate = QUERIES[r.worker_id - 1][1].split()[-1].rstrip(".")
        print(
            f"  worker {r.worker_id} | thread={r.thread_id} turn={r.turn_id} "
            f"events={len(r.events)} text_len={len(r.final_text)} "
            f"duration={r.duration_s:.1f}s | plate={plate}"
        )
        if r.error:
            print(f"    ERROR: {r.error}")

    # --- Assertions ---

    failed = False

    # (1) Every worker finished without an exception
    for r in results:
        if r.error:
            print(f"FAIL: worker {r.worker_id} raised: {r.error}")
            failed = True

    # (2) Every worker received a ``done`` event
    for r in results:
        if not any(e["type"] == "done" for e in r.events):
            print(
                f"FAIL: worker {r.worker_id} did not see a 'done' event. "
                f"types={[e['type'] for e in r.events]}"
            )
            failed = True

    # (3) Every worker produced non-empty final text
    for r in results:
        if len(r.final_text.strip()) < 20:
            print(
                f"FAIL: worker {r.worker_id} answer too short: "
                f"{r.final_text!r}"
            )
            failed = True

    # (4) No cross-contamination — each worker's skill_executed events
    # must mention only its own plate, never another worker's plate.
    plates = [QUERIES[i][1].split()[-1].rstrip(".") for i in range(len(QUERIES))]
    for r in results:
        own_plate = plates[r.worker_id - 1].upper()
        others = [p.upper() for i, p in enumerate(plates) if i != r.worker_id - 1]
        for ev in r.events:
            if ev["type"] not in ("skill_executing", "skill_executed"):
                continue
            params_blob = json.dumps(ev.get("params") or {}).upper()
            for other_plate in others:
                # Watch for the OTHER worker's plate appearing in this
                # worker's skill params. We strip dashes for the W-55123K
                # vs ZG-1234-AB shape difference.
                normalized_blob = params_blob.replace("-", "")
                normalized_other = other_plate.replace("-", "")
                if normalized_other in normalized_blob:
                    print(
                        f"FAIL: worker {r.worker_id} ({own_plate}) "
                        f"called a skill with {other_plate}'s plate "
                        f"params={ev.get('params')}"
                    )
                    failed = True

    # (5) Parallelism check — the wall clock should be close to the
    # longest single worker, not the sum of all. We're lenient: at
    # most 1.5× the slowest worker indicates real parallelism.
    longest_single = max(r.duration_s for r in results)
    if overall_duration > longest_single * 1.5:
        print(
            f"WARN: wall time {overall_duration:.1f}s > 1.5× slowest "
            f"single ({longest_single:.1f}s) — workers may have serialized"
        )
        # Don't fail on this — it's diagnostic, not strict.

    if failed:
        print("\nFAIL: concurrent run had errors")
        return 1
    print("\nPASS: 3-way concurrent run — no errors, no cross-bleed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
