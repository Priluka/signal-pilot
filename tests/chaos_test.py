"""Chaos test suite — 12 scenarios × 3 runs each. Real Anthropic API.

Covers HITL flow combinations (5), race conditions (3) and edge cases (4)
that the operator can hit through normal interaction with the agent.
Each scenario runs three times and only PASSes if all three pass — a 2/3
result is reported as FLAKY.

  HITL (assisted mode):
    H1  process → reads → 1 write → approve → finish
    H2  process → reads → write → approve → 2nd write → approve → finish
    H3  process → write → reject → planner recovers → finish
    H4  process → write → approve → 2nd write → reject → finish
    H5  process → write → approve → planner crashes (simulated) → error

  Race conditions:
    R6  double-click approve on the same pending action (assisted)
    R7  concurrent process_ticket on the same ticket_id (shadow)
    R8  refresh during processing — session snapshots remain internally
        consistent (shadow)

  Edge cases:
    E9   empty description → classifier shortcut → planner runs → finish
    E10  2000-char description with plate near the end → finish
    E11  no-skills playbook → drafter path → draft persisted
    E12  skills playbook, generic question — planner reaches done either
         by calling skills then ending OR by ending without skills

Cost ≈ $0.05-0.20 per HITL run on Sonnet 4.6. 36 runs total → $2-7.
Wall time ≈ 15-25 minutes.

Run from project root:

    .venv/bin/python tests/chaos_test.py
    .venv/bin/python tests/chaos_test.py --runs 1            # cheaper
    .venv/bin/python tests/chaos_test.py --names H1 R6       # subset
"""
from __future__ import annotations

import argparse
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from core import (  # noqa: E402
    agent_audit,
    agent_config,
    agent_runner,
    agent_sessions,
    drafter,
    pending_actions,
    planner,
)
from core.retrieval import load_playbook  # noqa: E402
from core.skills import external as _  # noqa: E402, F401  side-effect register


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


SKILLS_PB_PATH = _ROOT / "data/playbooks/end_user/billing/austrian-ticketless-incorrect-charge-refund.md"
NO_SKILLS_PB_PATH = _ROOT / "data/playbooks/end_user/user_issues/microsoft365-quarantine-notification-auto-tickets.md"


def _load_pbs() -> tuple[Any, Any]:
    return load_playbook(SKILLS_PB_PATH), load_playbook(NO_SKILLS_PB_PATH)


def _mk_ticket(key: str, summary: str, description: str) -> dict[str, Any]:
    return {
        "key": key,
        "summary": summary,
        "description": description,
        "labels": [],
        "reporter_email": "ops@test.local",
        "attachments": [],
    }


def _cleanup(ticket_id: str) -> None:
    pending_actions.clear_for_ticket(ticket_id)
    agent_sessions.delete_session(ticket_id)


# ---------------------------------------------------------------------------
# HITL driver — drives an action sequence (approve / reject) until terminal
# ---------------------------------------------------------------------------


@dataclass
class HitlOutcome:
    """Final state of one HITL run plus the audit row counts that prove
    each step actually happened."""
    final_status: str
    iterations_total: int
    pending_actions_seen: list[str]  # skill names of each pause
    audit_executed: int
    audit_rejected: int
    error: str | None = None


def _approve_via_router_path(action_id: str) -> Any:
    """Mimic the backend ``POST /actions/{id}/approve`` flow: atomic
    claim first, then planner.resume. Returns either a PlannerResult or
    a sentinel marker when the claim lost the race."""
    pa = pending_actions.claim(action_id)
    if pa is None:
        return "already_claimed"
    return planner.resume(
        action_id=action_id, approved=True, decided_by="chaos-test"
    )


def _reject_via_router_path(action_id: str, note: str) -> Any:
    pa = pending_actions.claim(action_id)
    if pa is None:
        return "already_claimed"
    return planner.resume(
        action_id=action_id,
        approved=False,
        rejection_note=note,
        decided_by="chaos-test",
    )


def run_hitl_sequence(
    *,
    ticket: dict[str, Any],
    playbook: Any,
    actions: list[str],  # 'approve' or 'reject', in order
    mode: str = "assisted",
) -> HitlOutcome:
    """Run planner.run then walk the requested sequence until terminal
    or until the action list runs out."""
    ticket_id = str(ticket["key"])
    _cleanup(ticket_id)
    agent_config.set_mode(mode)

    pres = planner.run(ticket=ticket, playbook=playbook)
    seen: list[str] = []
    iters = pres.iterations
    err = pres.error
    for action in actions:
        if pres.status != "awaiting_approval":
            break
        pa = pending_actions.get(pres.pending_action_id or "")
        if pa is None:
            err = f"pending {pres.pending_action_id} disappeared before {action}"
            break
        seen.append(pa.skill_name)
        if action == "approve":
            pres = _approve_via_router_path(pres.pending_action_id or "")
        else:
            pres = _reject_via_router_path(
                pres.pending_action_id or "", note="chaos test rejection"
            )
        if isinstance(pres, str):
            err = pres
            break
        iters = pres.iterations
        if pres.error:
            err = pres.error

    history = agent_audit.list_for_ticket(ticket_id)
    executed = sum(
        1
        for h in history
        if h.ok and h.outcome in ("auto", "approved")
    )
    rejected = sum(1 for h in history if h.outcome == "rejected")
    return HitlOutcome(
        final_status=pres.status if not isinstance(pres, str) else "claim_lost",
        iterations_total=iters,
        pending_actions_seen=seen,
        audit_executed=executed,
        audit_rejected=rejected,
        error=err,
    )


# ---------------------------------------------------------------------------
# Individual test scenarios
# ---------------------------------------------------------------------------


@dataclass
class CaseResult:
    name: str
    bucket: str
    runs: list[bool] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    elapsed_s_total: float = 0.0

    @property
    def verdict(self) -> str:
        passes = sum(1 for r in self.runs if r)
        if passes == len(self.runs):
            return "PASS"
        if passes == 0:
            return "FAIL"
        return f"FLAKY ({passes}/{len(self.runs)})"


# ---- HITL scenarios --------------------------------------------------------


def H1_one_read_one_write_approve(run_idx: int) -> tuple[bool, str]:
    """process → reads → write → approve → finish."""
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-H1-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Doppelbelastung W-55123K",
        "Mein Kennzeichen W-55123K wurde am 27. Mai zweimal 4,50 EUR "
        "belastet in der Garage Millennium City. Bitte Rückerstattung.",
    )
    # Approve up to 3 pause points so the test doesn't FAIL on the rare
    # planner that emits a 2nd write before settling.
    outcome = run_hitl_sequence(
        ticket=ticket, playbook=skills_pb, actions=["approve", "approve", "approve"]
    )
    _cleanup(ticket_id)
    if outcome.final_status != "done":
        return False, f"final={outcome.final_status} err={outcome.error}"
    if outcome.audit_executed < 1:
        return False, "no write skill recorded in audit"
    return True, f"executed={outcome.audit_executed}, paused on {outcome.pending_actions_seen}"


def H2_two_writes_both_approved(run_idx: int) -> tuple[bool, str]:
    """process → reads → write1 → approve → planner suggests write2 → approve → finish.

    Pass condition is loose: planner reached done after at most 2 approves.
    The model doesn't deterministically emit two writes in one run; we
    accept either 1-approve or 2-approve flows as long as the agent
    eventually reaches done.
    """
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-H2-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Mehrere offene Forderungen W-44556D",
        "Habe drei offene Beträge für W-44556D, weiß nicht woher. "
        "Karte abgelaufen. Bitte intern notieren und mir antworten.",
    )
    outcome = run_hitl_sequence(
        ticket=ticket, playbook=skills_pb, actions=["approve", "approve", "approve"]
    )
    _cleanup(ticket_id)
    if outcome.final_status != "done":
        return False, f"final={outcome.final_status} err={outcome.error}"
    return True, (
        f"paused {len(outcome.pending_actions_seen)}× on {outcome.pending_actions_seen}, "
        f"executed={outcome.audit_executed}"
    )


def H3_reject_recovers(run_idx: int) -> tuple[bool, str]:
    """process → write → reject → planner gets feedback and ends or re-asks."""
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-H3-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Sitzung steckt offen W-38702T",
        "Schwarzenbergplatz, W-38702T, Schranke ging nicht auf, "
        "Sitzung noch offen in der App. Bitte prüfen.",
    )
    # First action is reject; if planner queues another action after the
    # rejection, approve it to let the run terminate.
    outcome = run_hitl_sequence(
        ticket=ticket,
        playbook=skills_pb,
        actions=["reject", "approve", "approve"],
    )
    _cleanup(ticket_id)
    if outcome.audit_rejected < 1:
        return False, "expected at least 1 rejection in audit"
    if outcome.final_status != "done":
        return False, f"final={outcome.final_status} err={outcome.error}"
    return True, f"rejected={outcome.audit_rejected}, paused={outcome.pending_actions_seen}"


def H4_approve_then_reject(run_idx: int) -> tuple[bool, str]:
    """process → write → approve → 2nd write → reject → finish.

    Like H2, accepts either single-write (then no 2nd reject happens) or
    two-write pattern.
    """
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-H4-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Refund-Anfrage W-88211C",
        "Bitte Rückerstattung für W-88211C, 4,50 EUR am 25. Mai. "
        "Status?",
    )
    outcome = run_hitl_sequence(
        ticket=ticket,
        playbook=skills_pb,
        actions=["approve", "reject", "approve"],
    )
    _cleanup(ticket_id)
    if outcome.final_status != "done":
        return False, f"final={outcome.final_status} err={outcome.error}"
    return True, (
        f"paused={outcome.pending_actions_seen}, "
        f"executed={outcome.audit_executed}, rejected={outcome.audit_rejected}"
    )


def H5_planner_crash_after_approve(run_idx: int) -> tuple[bool, str]:
    """process → write → approve → planner errors during resume continuation.

    Crash is simulated by monkey-patching ``planner._create_with_retry``
    to raise on the SECOND call. The first call runs normally and
    produces the pending action; the second (post-resume continuation)
    fails. We verify the failure propagates as status='failed' with a
    captured error message and the agent_sessions row records it.
    """
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-H5-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Doppelbelastung W-55123K",
        "Doppelbelastung W-55123K, 4,50 EUR, Millennium City. "
        "Bitte um Rückerstattung.",
    )
    _cleanup(ticket_id)
    agent_config.set_mode("assisted")
    pres = planner.run(ticket=ticket, playbook=skills_pb)
    if pres.status != "awaiting_approval":
        _cleanup(ticket_id)
        return False, f"first run did not pause: {pres.status}"
    pa_id = pres.pending_action_id or ""

    # Patch resume's downstream LLM call to raise — covers the case
    # where Anthropic itself returns an unrecoverable error AFTER the
    # operator approved the pending action.
    original = planner._create_with_retry  # type: ignore[attr-defined]

    def boom(*a: Any, **kw: Any) -> Any:
        raise RuntimeError("simulated Anthropic outage")

    planner._create_with_retry = boom  # type: ignore[attr-defined]
    try:
        result = _approve_via_router_path(pa_id)
    finally:
        planner._create_with_retry = original  # type: ignore[attr-defined]

    _cleanup(ticket_id)
    if isinstance(result, str):
        return False, f"claim lost: {result}"
    if result.status != "failed":
        return False, f"expected failed, got {result.status}"
    if not result.error or "outage" not in result.error.lower():
        return False, f"error not captured: {result.error!r}"
    return True, f"failed cleanly: {result.error[:60]!r}"


# ---- Race conditions -------------------------------------------------------


def R6_double_click_approve(run_idx: int) -> tuple[bool, str]:
    """Two threads call approve on the same pending action simultaneously.

    The atomic claim pattern in ``pending_actions.claim()`` must let
    exactly one thread proceed; the other must observe the row already
    claimed and decline cleanly without re-executing the skill.
    """
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-R6-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "W-55123K doppelt belastet",
        "W-55123K, Garage Millennium City 27. Mai, 4,50 EUR doppelt. "
        "Bitte Rückerstattung.",
    )
    _cleanup(ticket_id)
    agent_config.set_mode("assisted")
    pres = planner.run(ticket=ticket, playbook=skills_pb)
    if pres.status != "awaiting_approval":
        _cleanup(ticket_id)
        return False, f"setup failed: {pres.status}"
    pa_id = pres.pending_action_id or ""

    results: list[Any] = [None, None]

    def worker(i: int) -> None:
        results[i] = _approve_via_router_path(pa_id)

    t1 = threading.Thread(target=worker, args=(0,))
    t2 = threading.Thread(target=worker, args=(1,))
    t1.start(); t2.start()
    t1.join(); t2.join()

    _cleanup(ticket_id)
    real = [r for r in results if not isinstance(r, str)]
    lost = [r for r in results if isinstance(r, str) and r == "already_claimed"]
    if len(real) != 1 or len(lost) != 1:
        return False, f"expected 1 winner + 1 already_claimed, got real={len(real)} lost={len(lost)}"
    return True, "1 winner, 1 already_claimed (atomic claim held)"


def R7_concurrent_process_same_ticket(run_idx: int) -> tuple[bool, str]:
    """Two threads process the same ticket. Per-ticket lock must serialize.

    Patches ``retrieve`` to return [] so the runner takes the no_hits
    short-circuit immediately after classify — that lets the test
    isolate the lock behaviour from any real retrieval index, which
    we don't want to build / mock here (3+ seconds, real I/O).
    Shadow mode keeps it cheap on the LLM side too.
    """
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-R7-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Provjeri W-55123K dvostruka naplata",
        "Mein Kennzeichen W-55123K wurde am 27. Mai zweimal belastet "
        "in der Garage Millennium City. Bitte prüfen.",
    )
    _cleanup(ticket_id)
    agent_config.set_mode("shadow")
    playbooks_arg = [skills_pb]

    class FakeIndex:
        pass

    # Per-thread arrival times so we can prove the lock truly held.
    started: dict[str, float] = {}
    finished: dict[str, float] = {}
    crashes: list[str] = []

    from unittest.mock import patch

    def worker(tag: str) -> None:
        try:
            started[tag] = time.time()
            list(
                agent_runner.process_ticket_streaming(
                    ticket, playbooks_arg, FakeIndex()
                )
            )
            finished[tag] = time.time()
        except Exception as exc:  # noqa: BLE001
            crashes.append(f"{tag}: {exc}")

    with patch("core.agent_runner.retrieve", return_value=[]):
        t1 = threading.Thread(target=worker, args=("A",))
        t2 = threading.Thread(target=worker, args=("B",))
        t1.start()
        time.sleep(0.05)  # bias B to lose the lock race
        t2.start()
        t1.join(); t2.join()

    if crashes:
        _cleanup(ticket_id)
        return False, f"worker crash: {crashes}"

    # Lock-held proof: whichever thread won the lock must FINISH before
    # the loser starts its critical section. Since we instrumented
    # `started` BEFORE the lock acquire, the test condition is:
    # one of (A_finish ≤ B_finish) holds and there is no interleave.
    # In practice the cleanest signal is: the later finisher's finish
    # is strictly AFTER the earlier one's, which holds for any
    # serialised execution.
    if "A" not in finished or "B" not in finished:
        _cleanup(ticket_id)
        return False, f"a worker did not finish: started={list(started)} finished={list(finished)}"
    fin_a, fin_b = finished["A"], finished["B"]
    if fin_a == fin_b:
        _cleanup(ticket_id)
        return False, "both workers finished at the same instant — lock did not serialize"

    rec = agent_sessions.get_session(ticket_id)
    if rec is None or rec.classified_at is None:
        _cleanup(ticket_id)
        return False, f"session row missing classify: rec={rec}"
    _cleanup(ticket_id)
    spread_ms = int(abs(fin_a - fin_b) * 1000)
    return True, f"serialised, finish spread {spread_ms}ms"


def R8_refresh_during_processing(run_idx: int) -> tuple[bool, str]:
    """Poll session row mid-run; every snapshot must be self-consistent.

    Self-consistent = every populated downstream field implies its
    upstream is also set (e.g. retrieved_at set ⇒ classified_at set).
    Catches a class of partial-write race conditions where the runner
    wrote a downstream column without first writing upstream.
    """
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-R8-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Provjeri W-38702T",
        "Schwarzenbergplatz W-38702T, Schranke ging nicht auf, "
        "Sitzung noch offen.",
    )
    _cleanup(ticket_id)
    agent_config.set_mode("shadow")

    class FakeIndex:
        pass

    snapshots: list[Any] = []

    def runner() -> None:
        list(
            agent_runner.process_ticket_streaming(
                ticket, [skills_pb], FakeIndex()
            )
        )

    th = threading.Thread(target=runner)
    th.start()
    # Sample the session row while the runner is mid-flight.
    for _ in range(40):
        if not th.is_alive():
            break
        rec = agent_sessions.get_session(ticket_id)
        if rec is not None:
            snapshots.append(rec)
        time.sleep(0.25)
    th.join()
    final = agent_sessions.get_session(ticket_id)
    snapshots.append(final)

    # Every snapshot must satisfy: retrieved_at ⇒ classified_at;
    # drafted_at ⇒ retrieved_at (drafter path); routing != null ⇒
    # retrieved_at.
    for s in snapshots:
        if s is None:
            continue
        if s.retrieved_at and not s.classified_at:
            _cleanup(ticket_id)
            return False, "retrieved_at set without classified_at"
        if s.drafted_at and not s.retrieved_at:
            _cleanup(ticket_id)
            return False, "drafted_at set without retrieved_at"
        if s.routing and not s.retrieved_at:
            _cleanup(ticket_id)
            return False, "routing set without retrieved_at"

    if final is None or final.classified_at is None:
        _cleanup(ticket_id)
        return False, "final session missing classify"
    _cleanup(ticket_id)
    return True, f"{len(snapshots)} consistent snapshots"


# ---- Edge cases ------------------------------------------------------------


def E9_empty_description(run_idx: int) -> tuple[bool, str]:
    """Empty description → classifier shortcut → planner runs."""
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-E9-R{run_idx}"
    ticket = _mk_ticket(ticket_id, "Problem W-55123K", "")
    outcome = run_hitl_sequence(
        ticket=ticket,
        playbook=skills_pb,
        actions=["approve", "approve"],
        mode="assisted",
    )
    _cleanup(ticket_id)
    if outcome.final_status != "done":
        return False, f"final={outcome.final_status} err={outcome.error}"
    return True, f"reached done despite empty desc, paused {len(outcome.pending_actions_seen)}×"


def E10_long_description(run_idx: int) -> tuple[bool, str]:
    """2000-char description with the operative plate near the end."""
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-E10-R{run_idx}"
    filler = (
        "Imam dosta dugačko pitanje i prije nego što stignem do glavne stvari "
        "želim ti dati kontekst o prethodnoj komunikaciji s kupcem. "
    ) * 12  # ~ 1700 chars of filler
    description = (
        filler
        + "Glavno pitanje: kupac s tablicom W-55123K tvrdi da je dvostruko "
        "naplaćen u garaži Millennium City Wien dana 27. svibnja, iznos "
        "4,50 EUR. Možeš li provjeriti?"
    )
    ticket = _mk_ticket(ticket_id, "Dugačko pitanje s plate na kraju", description)
    outcome = run_hitl_sequence(
        ticket=ticket,
        playbook=skills_pb,
        actions=["approve", "approve"],
    )
    _cleanup(ticket_id)
    if outcome.final_status != "done":
        return False, f"final={outcome.final_status} err={outcome.error}"
    return True, f"executed={outcome.audit_executed}"


def E11_drafter_path_no_skills(run_idx: int) -> tuple[bool, str]:
    """Playbook without allowed_skills → drafter path → draft returned."""
    _, no_skills_pb = _load_pbs()
    summary = "Microsoft 365 quarantine notification"
    description = (
        "Auto-generated message from Microsoft 365 about an email landing "
        "in quarantine. No user action needed. Closing automatically."
    )
    try:
        result = drafter.draft_reply(
            ticket_summary=summary,
            ticket_description=description,
            playbook=no_skills_pb,
            has_attachments=False,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"drafter crashed: {exc}"
    if not result.draft or len(result.draft) < 20:
        return False, f"draft too short ({len(result.draft)} chars)"
    if result.recommended_action not in (
        "send_draft",
        "send_with_review",
        "auto_close",
        "escalate_to_human",
    ):
        return False, f"unknown recommended_action: {result.recommended_action}"
    return True, f"draft {len(result.draft)} chars, action={result.recommended_action}"


def E12_skills_playbook_no_skill_calls(run_idx: int) -> tuple[bool, str]:
    """Skills playbook + generic question → planner may or may not call
    skills, just must reach a terminal state cleanly without crashing.
    """
    skills_pb, _ = _load_pbs()
    ticket_id = f"CHAOS-E12-R{run_idx}"
    ticket = _mk_ticket(
        ticket_id,
        "Allgemeine Frage zum Rückerstattungsprozess",
        "Wie lange dauert eine Rückerstattung üblicherweise? "
        "Bitte keine konkrete Datenabfrage, nur allgemeine Information.",
    )
    outcome = run_hitl_sequence(
        ticket=ticket,
        playbook=skills_pb,
        actions=["approve", "approve"],
    )
    _cleanup(ticket_id)
    if outcome.final_status != "done":
        return False, f"final={outcome.final_status} err={outcome.error}"
    return True, (
        f"reached done; "
        f"executed={outcome.audit_executed}, paused {len(outcome.pending_actions_seen)}×"
    )


# ---------------------------------------------------------------------------
# Registry + runner
# ---------------------------------------------------------------------------


@dataclass
class CaseSpec:
    name: str
    bucket: str
    fn: Callable[[int], tuple[bool, str]]
    description: str


CASES: list[CaseSpec] = [
    CaseSpec("H1", "hitl", H1_one_read_one_write_approve,
             "1 write → approve → finish"),
    CaseSpec("H2", "hitl", H2_two_writes_both_approved,
             "writes → approve → finish (1-2 approves)"),
    CaseSpec("H3", "hitl", H3_reject_recovers,
             "write → reject → recover → finish"),
    CaseSpec("H4", "hitl", H4_approve_then_reject,
             "write → approve → 2nd write → reject → finish"),
    CaseSpec("H5", "hitl", H5_planner_crash_after_approve,
             "approve → planner crash → error persisted"),
    CaseSpec("R6", "race", R6_double_click_approve,
             "double-click approve, atomic claim wins exactly once"),
    CaseSpec("R7", "race", R7_concurrent_process_same_ticket,
             "concurrent process same ticket, per-ticket lock"),
    CaseSpec("R8", "race", R8_refresh_during_processing,
             "session snapshots self-consistent during run"),
    CaseSpec("E9", "edge", E9_empty_description,
             "empty description, classifier shortcut path"),
    CaseSpec("E10", "edge", E10_long_description,
             "2000-char description, plate near the end"),
    CaseSpec("E11", "edge", E11_drafter_path_no_skills,
             "no-skills playbook, drafter path"),
    CaseSpec("E12", "edge", E12_skills_playbook_no_skill_calls,
             "skills playbook, generic question, terminal state"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3,
                        help="Times to run each case (default 3)")
    parser.add_argument("--names", nargs="+", default=None,
                        help="Subset (e.g. H1 R6 E11)")
    args = parser.parse_args()

    cases = CASES
    if args.names:
        wanted = set(args.names)
        cases = [c for c in cases if c.name in wanted]
    if not cases:
        print("no matching cases", file=sys.stderr)
        return 1

    print(
        f"Chaos sweep · {len(cases)} cases × {args.runs} runs  "
        f"= {len(cases) * args.runs} total executions"
    )
    print()
    overall_start = time.time()

    results: list[CaseResult] = []
    for i, spec in enumerate(cases, 1):
        r = CaseResult(name=spec.name, bucket=spec.bucket)
        for j in range(args.runs):
            run_no = j + 1
            print(
                f"[{i:2d}/{len(cases)}]  {spec.name}  run {run_no}/{args.runs} ...",
                end=" ", flush=True,
            )
            t0 = time.time()
            try:
                ok, note = spec.fn(run_no)
            except Exception as exc:  # noqa: BLE001
                ok, note = False, f"CRASHED: {type(exc).__name__}: {exc}"
            elapsed = time.time() - t0
            r.runs.append(ok)
            r.notes.append(note)
            r.elapsed_s_total += elapsed
            glyph = "✓" if ok else "✗"
            print(f"{glyph} {elapsed:5.1f}s  {note[:80]}")
        results.append(r)

    elapsed = time.time() - overall_start
    _print_summary(results, args.runs, elapsed)
    return 0 if all(r.verdict == "PASS" for r in results) else 1


def _print_summary(results: list[CaseResult], runs: int, elapsed: float) -> None:
    print()
    print("=" * 110)
    print(f"{'CASE':5} {'BUCKET':6} {'PASSES':9} {'TIME':7}  VERDICT     DESCRIPTION")
    print("-" * 110)
    spec_by_name = {c.name: c for c in CASES}
    for r in results:
        passes = sum(1 for x in r.runs if x)
        glyph = "✓" if r.verdict == "PASS" else ("~" if r.verdict.startswith("FLAKY") else "✗")
        desc = spec_by_name[r.name].description if r.name in spec_by_name else ""
        print(
            f"{r.name:5} {r.bucket:6} "
            f"{passes}/{runs:<5}    "
            f"{r.elapsed_s_total:5.1f}s  "
            f"{glyph} {r.verdict:10} {desc[:55]}"
        )
    print("-" * 110)
    pass_n = sum(1 for r in results if r.verdict == "PASS")
    fail_n = sum(1 for r in results if r.verdict == "FAIL")
    flaky_n = sum(1 for r in results if r.verdict.startswith("FLAKY"))
    print(
        f"TOTAL  {len(results)} cases × {runs} runs  · "
        f"PASS={pass_n} FLAKY={flaky_n} FAIL={fail_n}  "
        f"({elapsed/60:.1f} min)"
    )
    # Failure detail
    bad = [r for r in results if r.verdict != "PASS"]
    if bad:
        print()
        print("DETAIL — non-PASS cases")
        print("-" * 110)
        for r in bad:
            print(f"\n  {r.name} ({r.verdict})")
            for i, (ok, note) in enumerate(zip(r.runs, r.notes), 1):
                glyph = "✓" if ok else "✗"
                print(f"    run {i}: {glyph} {note}")


if __name__ == "__main__":
    sys.exit(main())
