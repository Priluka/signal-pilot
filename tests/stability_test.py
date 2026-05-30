"""Stability test — runs classifier + planner N times per plate and
reports consistency across runs.

For each plate (15 normal + 5 edge cases), executes ``--runs`` (default 5)
independent passes of:

1. ``classify_ticket(summary, description)`` — captures label + confidence
2. ``planner.run(ticket, playbook)`` — captures skills called, comment body

After N runs, aggregates per-plate metrics:

* **Classifier**     — label identical across runs? confidence min/max?
* **Skill set**      — same exact skills_called every run? Jaccard otherwise.
* **Comment phrases** — same subset of expected_phrases hit every run?
* **Verdict**        — STABLE / DRIFT / UNSTABLE based on the above.

Edge case section focuses on hallucination resistance: empty descriptions,
made-up plates that don't exist in any mock system, mixed-language tickets,
and the "country-prefix" typo (A-W-… → W-… plate not found unless agent
strips prefix).

Cost: ~$0.05–0.15 per planner run. 20 plates × 5 runs = ~$10–15.
Use ``--runs 2`` for cheaper iteration or ``--plates W-55123K`` to subset.

Run from project root:

    .venv/bin/python tests/stability_test.py
    .venv/bin/python tests/stability_test.py --runs 3
    .venv/bin/python tests/stability_test.py --plates W-55123K EDGE-empty-desc
    .venv/bin/python tests/stability_test.py --edge-only
"""
from __future__ import annotations

import argparse
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from core import agent_audit, agent_config, pending_actions, planner  # noqa: E402
from core.classifier import classify_ticket  # noqa: E402
from core.retrieval import load_playbook  # noqa: E402
from core.skills import external as _  # noqa: E402, F401  — side-effect register

from tests.mock_skills_grounding import CASES as NORMAL_CASES, PlateCase  # noqa: E402


# ---------------------------------------------------------------------------
# Edge cases — focused on classifier/planner brittleness
# ---------------------------------------------------------------------------


# Pick three normal-case plates as the substrate for edge case variants so
# we can compare "with full description" vs "with stripped description"
# without changing the underlying mock-data fixture.
EDGE_CASES: list[PlateCase] = [
    PlateCase(
        plate="EDGE-empty-desc",
        ticket_summary="Doppelbelastung W-55123K",
        ticket_description="",
        expected_skills={"bmove_user_lookup", "datatrans_transaction", "graylog_search"},
        expected_phrases=["W-55123K", "4,50", "4.50", "settled", "einmal", "only one"],
        story="Same plate as W-55123K but description is empty",
    ),
    PlateCase(
        plate="EDGE-one-word",
        ticket_summary="problem",
        ticket_description="W-55123K",
        expected_skills={"bmove_user_lookup"},
        expected_phrases=["W-55123K", "more info", "weitere", "details", "info"],
        story="One-word summary, only a plate in description — agent must ask back",
    ),
    PlateCase(
        plate="EDGE-nonexistent",
        ticket_summary="Doppelte Belastung W-99999X",
        ticket_description=(
            "Mein Kennzeichen W-99999X wurde gestern doppelt belastet "
            "in der Garage Millennium City. Bitte um Rückerstattung."
        ),
        # Plate doesn't exist anywhere — agent should call lookups, get
        # found=false everywhere, then ASK for more info rather than invent
        # a transaction. Skills "called" must be at least one of the
        # lookups; data populated must be empty.
        expected_skills={"bmove_user_lookup"},
        expected_phrases=[
            "not found",
            "nicht gefunden",
            "keine",
            "no record",
            "more info",
            "weitere",
            "exakte",
            "kennzeichen prüfen",
        ],
        story="Made-up plate; agent must NOT hallucinate a transaction",
    ),
    PlateCase(
        plate="EDGE-prefix-typo",
        ticket_summary="Charge for parking A-W-38702T",
        ticket_description=(
            "I was charged for parking at Schwarzenbergplatz but I added "
            "my plate as A-W-38702T in the app. Session is still active."
        ),
        # Real plate is W-38702T; customer wrote A-W-38702T (country prefix).
        # Agent must either strip the prefix or report not-found honestly.
        expected_skills={"bmove_user_lookup", "skidata_session_lookup"},
        expected_phrases=[
            "W-38702T",
            "without",
            "ohne",
            "präfix",
            "prefix",
            "format",
            "not found",
            "nicht gefunden",
            "schwarzenbergplatz",
        ],
        story="Country-prefix typo (A-W-…) — agent should strip prefix or ask",
    ),
    PlateCase(
        plate="EDGE-mixed-lang",
        ticket_summary="Refund please",
        ticket_description=(
            "Tablica W-55123K, danas Millennium City. Two charges 4.50 EUR "
            "but I only parked once. Können Sie das zurückerstatten?"
        ),
        expected_skills={"bmove_user_lookup", "datatrans_transaction", "graylog_search"},
        expected_phrases=["4,50", "4.50", "settled", "einmal", "only one", "millennium"],
        story="Mixed HR/EN/DE in one ticket — classifier+planner stability",
    ),
]


ALL_CASES: list[PlateCase] = NORMAL_CASES + EDGE_CASES


# ---------------------------------------------------------------------------
# Per-run capture
# ---------------------------------------------------------------------------


@dataclass
class RunResult:
    """One pass of (classify + plan) for a plate."""
    label: str = ""
    confidence: float = 0.0
    called_skills: set[str] = field(default_factory=set)
    skills_with_data: set[str] = field(default_factory=set)
    comment_body: str = ""
    matched_phrases: set[str] = field(default_factory=set)
    planner_status: str = ""
    iterations: int = 0
    elapsed_s: float = 0.0
    error: str | None = None


@dataclass
class PlateAggregate:
    """N runs collapsed into a per-plate stability verdict."""
    plate: str
    story: str
    runs: list[RunResult] = field(default_factory=list)
    expected_skills: set[str] = field(default_factory=set)

    # Derived after all runs:
    classifier_stable: bool = False  # same label every run
    classifier_label: str = ""
    confidence_min: float = 0.0
    confidence_max: float = 0.0
    skills_identical: bool = False  # exact set match across runs
    skills_intersection: set[str] = field(default_factory=set)
    skills_union: set[str] = field(default_factory=set)
    skills_jaccard: float = 1.0  # 1.0 = identical, 0.0 = no overlap
    phrases_identical: bool = False
    phrases_intersection: set[str] = field(default_factory=set)
    bodies_distinct_starts: int = 0  # rough variance proxy
    median_elapsed_s: float = 0.0
    error_count: int = 0
    verdict: str = ""

    def finalize(self) -> None:
        # Classifier
        labels = [r.label for r in self.runs if not r.error]
        if labels:
            self.classifier_stable = len(set(labels)) == 1
            self.classifier_label = labels[0] if self.classifier_stable else "MIXED"
        confs = [r.confidence for r in self.runs if not r.error and r.confidence > 0]
        if confs:
            self.confidence_min = min(confs)
            self.confidence_max = max(confs)
        # Skills
        skill_sets = [r.called_skills for r in self.runs if not r.error]
        if skill_sets:
            self.skills_intersection = set.intersection(*skill_sets) if skill_sets else set()
            self.skills_union = set.union(*skill_sets) if skill_sets else set()
            self.skills_identical = all(s == skill_sets[0] for s in skill_sets[1:])
            if self.skills_union:
                self.skills_jaccard = len(self.skills_intersection) / len(self.skills_union)
        # Phrases
        phrase_sets = [r.matched_phrases for r in self.runs if not r.error]
        if phrase_sets:
            self.phrases_intersection = set.intersection(*phrase_sets) if phrase_sets else set()
            self.phrases_identical = all(p == phrase_sets[0] for p in phrase_sets[1:])
        # Body variance — count distinct first-120-char prefixes
        starts = {r.comment_body[:120].strip() for r in self.runs if r.comment_body}
        self.bodies_distinct_starts = len(starts)
        # Elapsed
        elapsed = [r.elapsed_s for r in self.runs if not r.error]
        self.median_elapsed_s = statistics.median(elapsed) if elapsed else 0.0
        self.error_count = sum(1 for r in self.runs if r.error)
        # Verdict
        if self.error_count == len(self.runs):
            self.verdict = "CRASHED"
        elif (
            self.classifier_stable
            and self.skills_identical
            and self.phrases_identical
            and self.bodies_distinct_starts <= 2
        ):
            self.verdict = "STABLE"
        elif self.classifier_stable and self.skills_jaccard >= 0.66:
            self.verdict = "DRIFT"
        else:
            self.verdict = "UNSTABLE"


# ---------------------------------------------------------------------------
# Run logic
# ---------------------------------------------------------------------------


def _load_test_playbook():
    return load_playbook(
        _ROOT
        / "data/playbooks/end_user/integrations/parking-fine-received-despite-valid-payment.md"
    )


def _data_is_populated(data: dict | None) -> bool:
    if not data:
        return False
    if data.get("found") is True:
        return True
    if data.get("total_results", 0) > 0:
        return True
    if (
        data.get("user") is not None
        or data.get("transaction") is not None
        or data.get("session") is not None
    ):
        return True
    return False


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_one_pass(case: PlateCase, ticket_id: str, playbook) -> RunResult:
    """Single classifier+planner pass for one plate."""
    res = RunResult()
    pending_actions.clear_for_ticket(ticket_id)

    # 1. Classify
    try:
        cls = classify_ticket(
            summary=case.ticket_summary,
            description=case.ticket_description,
            reporter_email=None,
            labels=[],
        )
        res.label = cls.label
        res.confidence = cls.confidence
    except Exception as exc:  # noqa: BLE001
        res.error = f"classifier_crashed: {exc}"
        return res

    # If classifier says non-support, planner wouldn't run in production
    # either. Record and stop.
    if cls.label != "support_request":
        return res

    # 2. Plan
    ticket = {
        "key": ticket_id,
        "summary": case.ticket_summary,
        "description": case.ticket_description,
        "labels": [],
    }
    started_at_iso = _now_iso()
    started = time.time()
    try:
        result = planner.run(ticket=ticket, playbook=playbook)
    except Exception as exc:  # noqa: BLE001
        res.error = f"planner_crashed: {exc}"
        res.elapsed_s = time.time() - started
        return res
    res.elapsed_s = time.time() - started
    res.planner_status = result.status
    res.iterations = result.iterations
    if result.error:
        res.error = result.error

    # 3. Inspect audit for skills called
    history = [
        h for h in agent_audit.list_for_ticket(ticket_id) if h.decided_at >= started_at_iso
    ]
    res.called_skills = {h.skill_name for h in history if h.outcome == "auto"}
    res.skills_with_data = {
        h.skill_name
        for h in history
        if h.outcome == "auto" and h.ok and _data_is_populated(h.result_data)
    }

    # 4. Pull paused public comment + phrase matches
    pa_list = pending_actions.list_for_ticket(ticket_id)
    for pa in pa_list:
        if pa.skill_name == "jira_add_public_comment":
            res.comment_body = str(pa.skill_input.get("body", "")) or ""
            break
    if res.comment_body:
        cl = res.comment_body.lower()
        res.matched_phrases = {p for p in case.expected_phrases if p.lower() in cl}

    pending_actions.clear_for_ticket(ticket_id)
    return res


def run_plate(case: PlateCase, runs: int, playbook) -> PlateAggregate:
    """N independent passes for one plate; collapse to PlateAggregate."""
    agg = PlateAggregate(
        plate=case.plate, story=case.story, expected_skills=set(case.expected_skills)
    )
    for i in range(runs):
        ticket_id = f"STAB-{case.plate.replace('-', '_')}-{i + 1}"
        r = run_one_pass(case, ticket_id, playbook)
        agg.runs.append(r)
        # Inline progress so the operator sees something while the sweep
        # is in flight (could be ~15 min for the full run).
        status = "ok" if not r.error else "ERR"
        skill_count = len(r.called_skills)
        print(
            f"    run {i + 1}/{runs}  {status:3s}  label={r.label:18s} "
            f"conf={r.confidence:.2f}  skills={skill_count}  "
            f"phrases={len(r.matched_phrases)}/{len(case.expected_phrases)}  "
            f"{r.elapsed_s:.1f}s"
            + (f"  ({r.error[:60]})" if r.error else ""),
            flush=True,
        )
    agg.finalize()
    return agg


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _verdict_glyph(v: str) -> str:
    return {"STABLE": "✓", "DRIFT": "~", "UNSTABLE": "✗", "CRASHED": "!"}.get(v, "?")


def print_results(aggs: list[PlateAggregate], runs: int) -> None:
    print()
    print("=" * 132)
    print(
        f"{'PLATE':22} {'CLS':4} {'LABEL':18} {'CONF':12} "
        f"{'SKILLS':18} {'JACCARD':8} {'PHRASES':10} {'BODY-VAR':9} {'VERDICT':10}  STORY"
    )
    print("-" * 132)
    for a in aggs:
        if a.error_count == len(a.runs):
            print(
                f"{a.plate:22} {'-':4} {'(all runs errored)':18} "
                f"{'-':12} {'-':18} {'-':8} {'-':10} {'-':9} "
                f"{_verdict_glyph(a.verdict)} {a.verdict:8}  {a.story[:50]}"
            )
            continue
        cls_glyph = "✓" if a.classifier_stable else "✗"
        conf_str = (
            f"{a.confidence_min:.2f}-{a.confidence_max:.2f}"
            if a.confidence_min != a.confidence_max
            else f"{a.confidence_min:.2f}"
        )
        skills_glyph = "✓" if a.skills_identical else "~"
        skill_str = f"{skills_glyph} {len(a.skills_intersection)}/{len(a.skills_union)}"
        phrases_str = (
            f"{'✓' if a.phrases_identical else '~'} {len(a.phrases_intersection)}"
        )
        body_str = f"{a.bodies_distinct_starts}/{runs}"
        print(
            f"{a.plate:22} {cls_glyph:4} {a.classifier_label:18} {conf_str:12} "
            f"{skill_str:18} {a.skills_jaccard:8.2f} {phrases_str:10} "
            f"{body_str:9} {_verdict_glyph(a.verdict)} {a.verdict:8}  {a.story[:50]}"
        )

    # Aggregate summary
    print("-" * 132)
    n = len(aggs)
    stable = sum(1 for a in aggs if a.verdict == "STABLE")
    drift = sum(1 for a in aggs if a.verdict == "DRIFT")
    unstable = sum(1 for a in aggs if a.verdict == "UNSTABLE")
    crashed = sum(1 for a in aggs if a.verdict == "CRASHED")
    cls_unstable = [a for a in aggs if not a.classifier_stable and a.verdict != "CRASHED"]
    skill_unstable = [a for a in aggs if not a.skills_identical and a.verdict != "CRASHED"]
    print(
        f"TOTAL  {n} plates × {runs} runs  · "
        f"stable {stable}  drift {drift}  unstable {unstable}  crashed {crashed}"
    )
    if cls_unstable:
        print(
            f"  classifier flipped on: "
            + ", ".join(a.plate for a in cls_unstable)
        )
    if skill_unstable:
        print(
            f"  skill set varied on  : "
            + ", ".join(a.plate for a in skill_unstable)
        )
    print()
    # Detail section for non-stable plates so the reader can see WHY.
    interesting = [a for a in aggs if a.verdict != "STABLE"]
    if interesting:
        print("DETAIL — non-stable plates")
        print("-" * 132)
        for a in interesting:
            print(f"  {a.plate}  ({a.verdict})  {a.story}")
            if not a.classifier_stable:
                seen = {r.label for r in a.runs if r.label}
                print(f"    classifier labels seen: {sorted(seen)}")
            if not a.skills_identical:
                print(
                    f"    intersection (always called): {sorted(a.skills_intersection)}"
                )
                print(
                    f"    union (called at least once): {sorted(a.skills_union)}"
                )
                # Show per-run divergence
                for i, r in enumerate(a.runs, 1):
                    extra = r.called_skills - a.skills_intersection
                    if extra:
                        print(f"      run {i} extra: {sorted(extra)}")
            if a.bodies_distinct_starts > 2:
                print(
                    f"    body openings varied: {a.bodies_distinct_starts} distinct first-120-char prefixes"
                )
            if a.error_count:
                errs = [r.error for r in a.runs if r.error]
                print(f"    errors: {errs}")
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--runs",
        type=int,
        default=5,
        help="Number of passes per plate (default 5)",
    )
    parser.add_argument(
        "--plates",
        nargs="+",
        default=None,
        help="Subset of plate identifiers to run (e.g. W-55123K EDGE-empty-desc)",
    )
    parser.add_argument(
        "--edge-only",
        action="store_true",
        help="Run only the edge-case plates",
    )
    parser.add_argument(
        "--normal-only",
        action="store_true",
        help="Run only the 15 normal plates (skip edge cases)",
    )
    args = parser.parse_args()

    if args.edge_only:
        cases = EDGE_CASES
    elif args.normal_only:
        cases = NORMAL_CASES
    else:
        cases = ALL_CASES
    if args.plates:
        wanted = set(args.plates)
        cases = [c for c in cases if c.plate in wanted]
    if not cases:
        print("no matching plates", file=sys.stderr)
        return 1

    agent_config.set_mode("assisted")
    playbook = _load_test_playbook()

    print(
        f"Stability sweep · {len(cases)} plates × {args.runs} runs "
        f"= {len(cases) * args.runs} planner runs"
    )
    print(
        "Each planner run = 3–8 Anthropic calls (~$0.05–0.15). "
        "Wall time ~30s per run."
    )
    print()

    aggs: list[PlateAggregate] = []
    sweep_start = time.time()
    for i, case in enumerate(cases, 1):
        print(f"[{i}/{len(cases)}]  {case.plate}  — {case.story[:70]}")
        agg = run_plate(case, args.runs, playbook)
        aggs.append(agg)
    sweep_elapsed = time.time() - sweep_start

    print_results(aggs, args.runs)
    print(f"Total wall time: {sweep_elapsed / 60:.1f} min")
    # Exit non-zero if anything was unstable so CI can flag it.
    return 0 if all(a.verdict in ("STABLE", "DRIFT") for a in aggs) else 1


if __name__ == "__main__":
    sys.exit(main())
