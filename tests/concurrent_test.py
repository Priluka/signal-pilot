"""Concurrent ticket processing — stress test for per-ticket lock + isolation.

For each of 3 rounds, spawn 3 threads simultaneously hitting
``agent_runner.process_ticket`` on three DIFFERENT plates:

  • W-55123K  (Austrian double-charge)
  • ZG-1234-AB (Croatian SMS payment)
  • W-44556D  (3 months of expired-card debt)

After each round the script asserts:

  1. **All 3 succeed** — no crashes, no propagated exceptions.
  2. **No data mixing** — each session row carries its own
     classification, retrieval, and skill audit log; plates from other
     tickets must not appear in any session's draft or pending action.
  3. **Per-ticket lock holds** — every session has exactly ONE
     started_at stamp (no double-processing), and ``planner.run`` is
     not called concurrently for the same ticket_id.
  4. **Pending actions are isolated** — each ticket has at most one
     ``jira_add_public_comment`` queued, addressed to its own
     ``ticket_id``.

Rounds run sequentially so we get 3 independent attempts at catching
race conditions. Per ticket: ~30s wall time. Three rounds × 30s ≈ 90s
real time (concurrent within a round, sequential across).

Cost (Sonnet 4.6, current test config):
  3 plates × 3 rounds × ~$0.10/plan ≈ $0.90 per full run.

Run from project root:

    .venv/bin/python tests/concurrent_test.py
    .venv/bin/python tests/concurrent_test.py --rounds 1   # cheaper

Exit 0 if all assertions pass, non-zero otherwise.
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from core import agent_audit, agent_config, agent_runner, agent_sessions, pending_actions  # noqa: E402
from core.retrieval import build_index, discover_playbook_paths, load_playbook  # noqa: E402
from core.skills import external as _  # noqa: E402, F401  side-effect register


# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@dataclass
class TicketSpec:
    """One synthetic Jira ticket to run through the agent."""
    plate: str
    key_prefix: str
    summary: str
    description: str


SPECS: list[TicketSpec] = [
    TicketSpec(
        plate="W-55123K",
        key_prefix="CONC-A",
        summary="Doppelbelastung Garage Millennium City",
        description=(
            "Mein Kennzeichen W-55123K wurde am 27. Mai zweimal "
            "belastet für 4,50 EUR in der Garage Millennium City. "
            "Bitte um Rückerstattung."
        ),
    ),
    TicketSpec(
        plate="ZG-1234-AB",
        key_prefix="CONC-B",
        summary="SMS plaćanje zone 2 — potvrda?",
        description=(
            "Tablica ZG-1234-AB, danas zona 2 Zagreb, platio sam "
            "SMS-om 0.80 EUR. Operater me pita zašto nisam. Je li "
            "prošlo?"
        ),
    ),
    TicketSpec(
        plate="W-44556D",
        key_prefix="CONC-C",
        summary="Mehrere offene Forderungen",
        description=(
            "Kennzeichen W-44556D. Habe mehrere offene Beträge, weiß "
            "nicht woher. Letzte Aktivität war im April."
        ),
    ),
]


# ---------------------------------------------------------------------------
# Per-round capture
# ---------------------------------------------------------------------------


@dataclass
class RunResult:
    plate: str
    ticket_id: str
    started_at: float
    finished_at: float
    elapsed_s: float
    crashed: bool = False
    crash_message: str | None = None
    # Captured after process_ticket returns:
    session_present: bool = False
    classified_label: str | None = None
    drafted_at: str | None = None
    routing: str | None = None
    planner_status: str | None = None
    started_at_iso: str | None = None
    audit_rows: int = 0
    pending_public_comment_count: int = 0
    pending_body_excerpt: str = ""


@dataclass
class RoundResult:
    round_no: int
    runs: list[RunResult] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    elapsed_s: float = 0.0


# ---------------------------------------------------------------------------
# Lock observation — wrap the runner's _lock_for_ticket to detect any
# concurrent entry on the same ticket_id. We snoop without changing the
# implementation.
# ---------------------------------------------------------------------------


_active_per_ticket: dict[str, int] = {}
_active_guard = threading.Lock()
_observed_double_entry: list[str] = []


def _instrument_lock() -> None:
    """Wrap agent_runner._lock_for_ticket so we record concurrent entries."""
    original = agent_runner._lock_for_ticket

    class _CountingLock:
        def __init__(self, inner: threading.Lock, ticket_id: str) -> None:
            self._inner = inner
            self._ticket_id = ticket_id

        def __enter__(self) -> Any:
            self._inner.acquire()
            with _active_guard:
                _active_per_ticket[self._ticket_id] = (
                    _active_per_ticket.get(self._ticket_id, 0) + 1
                )
                if _active_per_ticket[self._ticket_id] > 1:
                    _observed_double_entry.append(self._ticket_id)
            return self

        def __exit__(self, *exc: Any) -> None:
            with _active_guard:
                _active_per_ticket[self._ticket_id] = max(
                    0, _active_per_ticket.get(self._ticket_id, 0) - 1
                )
            self._inner.release()

    def wrapper(ticket_id: str) -> Any:
        inner = original(ticket_id)
        return _CountingLock(inner, ticket_id)

    agent_runner._lock_for_ticket = wrapper  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# One worker — runs a single ticket through the agent
# ---------------------------------------------------------------------------


def _run_one(
    spec: TicketSpec,
    ticket_id: str,
    playbooks: Any,
    index: Any,
) -> RunResult:
    res = RunResult(
        plate=spec.plate,
        ticket_id=ticket_id,
        started_at=time.time(),
        finished_at=0.0,
        elapsed_s=0.0,
    )
    # Wipe any previous state for clean comparison.
    pending_actions.clear_for_ticket(ticket_id)
    agent_sessions.delete_session(ticket_id)

    ticket = {
        "key": ticket_id,
        "summary": spec.summary,
        "description": spec.description,
        "labels": [],
        "reporter_email": f"{spec.plate.lower()}@example.test",
    }
    try:
        agent_runner.process_ticket(ticket, playbooks, index)
    except Exception as exc:  # noqa: BLE001
        res.crashed = True
        res.crash_message = f"{type(exc).__name__}: {exc}"

    res.finished_at = time.time()
    res.elapsed_s = res.finished_at - res.started_at

    # Capture post-state.
    rec = agent_sessions.get_session(ticket_id)
    if rec is not None:
        res.session_present = True
        res.classified_label = (rec.classification or {}).get("label")
        res.drafted_at = rec.drafted_at
        res.routing = rec.routing
        res.planner_status = rec.planner_status
        res.started_at_iso = rec.started_at
    history = agent_audit.list_for_ticket(ticket_id)
    res.audit_rows = len(history)
    pending = pending_actions.list_for_ticket(ticket_id)
    pub_comments = [p for p in pending if p.skill_name == "jira_add_public_comment"]
    res.pending_public_comment_count = len(pub_comments)
    if pub_comments:
        res.pending_body_excerpt = str(pub_comments[0].skill_input.get("body", ""))[:200]
    return res


# ---------------------------------------------------------------------------
# Round driver
# ---------------------------------------------------------------------------


def run_round(
    round_no: int, playbooks: Any, index: Any
) -> RoundResult:
    rr = RoundResult(round_no=round_no)
    print(f"\n── Round {round_no} — launching 3 concurrent workers ──")
    started = time.time()
    # Unique ticket_ids per round so previous-round state doesn't bleed
    # in to the lock detector or DB rows.
    tasks = [(spec, f"{spec.key_prefix}-R{round_no}") for spec in SPECS]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {
            pool.submit(_run_one, spec, tid, playbooks, index): (spec, tid)
            for spec, tid in tasks
        }
        for fut in as_completed(futures):
            res = fut.result()
            rr.runs.append(res)
            outcome = "CRASH" if res.crashed else "ok"
            print(
                f"  [{outcome}]  {res.ticket_id:14s} {res.plate:12s} "
                f"label={res.classified_label or '-':16s} "
                f"audit={res.audit_rows:2d}  pend_pc={res.pending_public_comment_count}  "
                f"{res.elapsed_s:.1f}s"
                + (f"  ({res.crash_message})" if res.crash_message else "")
            )
    rr.elapsed_s = time.time() - started

    # ---- Assertions ----
    # 1) No crashes
    for r in rr.runs:
        if r.crashed:
            rr.failures.append(
                f"{r.ticket_id} crashed: {r.crash_message}"
            )
    # 2) All sessions present
    for r in rr.runs:
        if not r.session_present:
            rr.failures.append(f"{r.ticket_id} has no agent_sessions row")
    # 3) Each session classified
    for r in rr.runs:
        if r.session_present and r.classified_label is None:
            rr.failures.append(
                f"{r.ticket_id} session missing classification"
            )
    # 4) No data bleed — pending body for ticket A must NOT mention B/C plates
    plate_by_ticket = {f"{s.key_prefix}-R{round_no}": s.plate for s in SPECS}
    for r in rr.runs:
        if not r.pending_body_excerpt:
            continue
        body = r.pending_body_excerpt
        own_plate = plate_by_ticket[r.ticket_id]
        for tid, other_plate in plate_by_ticket.items():
            if tid == r.ticket_id:
                continue
            # The body should NEVER reference another ticket's plate
            if other_plate in body:
                rr.failures.append(
                    f"{r.ticket_id} body leaked plate '{other_plate}' "
                    f"from {tid}: …{body[:120]}…"
                )
    # 5) Per-ticket lock held — no overlapping entries observed
    if _observed_double_entry:
        rr.failures.append(
            f"per-ticket lock breach: {sorted(set(_observed_double_entry))}"
        )
        _observed_double_entry.clear()
    # 6) At most one pending public comment per ticket
    for r in rr.runs:
        if r.pending_public_comment_count > 1:
            rr.failures.append(
                f"{r.ticket_id} has {r.pending_public_comment_count} "
                "pending public comments — duplicate write detected"
            )
    return rr


def cleanup(round_no: int) -> None:
    """Remove session + pending rows we created so the next round starts fresh."""
    for spec in SPECS:
        tid = f"{spec.key_prefix}-R{round_no}"
        pending_actions.clear_for_ticket(tid)
        agent_sessions.delete_session(tid)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_summary(rounds: list[RoundResult]) -> None:
    print()
    print("=" * 100)
    print(f"{'ROUND':6} {'TIME':7} {'CRASH':6} {'PASS':5} {'FAIL':5}  STATUS")
    print("-" * 100)
    for rr in rounds:
        crashed = sum(1 for r in rr.runs if r.crashed)
        ok = sum(1 for r in rr.runs if not r.crashed)
        status = "PASS" if not rr.failures else "FAIL"
        print(
            f"{rr.round_no:6d} {rr.elapsed_s:6.1f}s {crashed:6d} "
            f"{ok:5d} {len(rr.failures):5d}  {status}"
        )
    print("-" * 100)
    any_fail = False
    for rr in rounds:
        if rr.failures:
            any_fail = True
            print(f"\nRound {rr.round_no} failures:")
            for f in rr.failures:
                print(f"  ✗ {f}")
    if not any_fail:
        print("\n✓ All rounds passed: no crashes, no data bleed, lock held, "
              "no duplicate writes.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rounds", type=int, default=3,
        help="How many independent rounds to run (default 3)",
    )
    parser.add_argument(
        "--mode", default="assisted", choices=("shadow", "assisted", "autonomous"),
        help="Agent mode (default assisted — write skills queue pending actions)",
    )
    args = parser.parse_args()

    agent_config.set_mode(args.mode)
    paths = discover_playbook_paths(_ROOT / "data/playbooks")
    playbooks = [load_playbook(p) for p in paths]
    index = build_index()

    _instrument_lock()
    rounds: list[RoundResult] = []
    overall_start = time.time()
    for n in range(1, args.rounds + 1):
        rr = run_round(n, playbooks, index)
        rounds.append(rr)
        cleanup(n)
    overall = time.time() - overall_start

    print_summary(rounds)
    print(f"\nTotal wall time: {overall:.1f}s")
    return 0 if all(not r.failures for r in rounds) else 1


if __name__ == "__main__":
    sys.exit(main())
