"""Mock-skills E2E grounding test.

For each of the 15 mock plates, builds a synthetic ticket, runs the
planner against the parking-fine playbook (which has all 9
``allowed_skills`` enabled), and checks three things:

1. **Skills called** — the read skills that have data for this plate
   were actually called by Claude.
2. **Skills returned data** — those calls returned a populated payload
   (``found: true`` or non-zero hits).
3. **Comment grounded** — the public-comment body Claude proposed
   contains at least one piece of data from the mock systems (amount,
   plate, status word, session id, etc.).

Output is one row per plate plus a verdict summary at the bottom.
Each plate costs one real planner run (~$0.05–0.15 of Claude tokens).
Total wall time roughly 8–10 minutes for the whole sweep.

Run from the project root:

    .venv/bin/python tests/mock_skills_grounding.py
    .venv/bin/python tests/mock_skills_grounding.py --plates W-55123K W-44556D
"""
from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from core import agent_audit, agent_config, pending_actions, planner  # noqa: E402
from core.retrieval import load_playbook  # noqa: E402
from core.skills import external as _  # noqa: E402, F401  — side-effect register


# ---------------------------------------------------------------------------
# Test cases — one per mock plate
# ---------------------------------------------------------------------------


@dataclass
class PlateCase:
    plate: str
    ticket_summary: str
    ticket_description: str
    expected_skills: set[str]  # subset of read skills that have data for this plate
    expected_phrases: list[str]  # any one match = grounded (case-insensitive)
    story: str  # short note for the summary table


CASES: list[PlateCase] = [
    PlateCase(
        plate="W-55123K",
        ticket_summary="Doppelbelastung Garage Millennium City",
        ticket_description=(
            "Mein Kennzeichen W-55123K wurde am 27. Mai zweimal belastet "
            "für 4,50 EUR in der Garage Millennium City. Bitte Rückerstattung."
        ),
        expected_skills={"bmove_user_lookup", "datatrans_transaction", "graylog_search"},
        expected_phrases=["4,50", "4.50", "settled", "einmal", "only one", "nur eine", "once"],
        story="Customer claims double charge; data shows only one settled",
    ),
    PlateCase(
        plate="W-38702T",
        ticket_summary="Parkschranke öffnet sich nicht beim Verlassen",
        ticket_description=(
            "Kennzeichen W-38702T, gestern Schwarzenbergplatz. Beim Reinfahren "
            "alles OK aber beim Ausfahren ging die Schranke nicht auf, "
            "Personal musste manuell öffnen. Sitzung noch offen?"
        ),
        expected_skills={"skidata_session_lookup", "graylog_search"},
        expected_phrases=["open", "offen", "lpr", "schranke", "manual", "manuell", "schwarzenbergplatz"],
        story="LPR failed on exit, session still open",
    ),
    PlateCase(
        plate="ZG-1234-AB",
        ticket_summary="SMS plaćanje zone 2 — potvrda?",
        ticket_description=(
            "Tablica ZG-1234-AB, danas zona 2 Zagreb, platio sam SMS-om "
            "0.80 EUR. Operater me pita zašto nisam. Je li prošlo?"
        ),
        expected_skills={"parkis_lookup", "graylog_search"},
        expected_phrases=["0,80", "0.80", "zone 2", "sms", "active", "primljen", "received"],
        story="SMS payment confirmed by ParkIS",
    ),
    PlateCase(
        plate="ZG-7777-XY",
        ticket_summary="Ne mogu platiti aplikacijom",
        ticket_description=(
            "Tablica ZG-7777-XY, više puta sam pokušao platiti parking "
            "preko Bmove aplikacije, kartica VISA *0192. Kaže greška. "
            "Imam li nešto neplaćeno?"
        ),
        expected_skills={"bmove_user_lookup", "datatrans_transaction", "graylog_search"},
        expected_phrases=["expired", "abgelaufen", "istekla", "12.40", "12,40", "card"],
        story="Card EXPIRED, outstanding debt 12.40",
    ),
    PlateCase(
        plate="W-12345B",
        ticket_summary="Naplata iako nisam parkirao",
        ticket_description=(
            "Naplaćeno mi je 2,50 EUR za garažu Kaptol Center Zagreb na "
            "tablicu W-12345B, ali nisam parkirao — samo sam prošao "
            "kroz nju. Zašto se naplaćuje?"
        ),
        expected_skills={"bmove_user_lookup", "skidata_session_lookup", "graylog_search"},
        expected_phrases=["2,50", "2.50", "kaptol", "5 minutes", "5 minuten", "minimum", "drove through", "prošao"],
        story="Drove through garage, charged minimum tariff",
    ),
    PlateCase(
        plate="SK-334AB",
        ticket_summary="Schranke geht nicht auf — slowakisches Kennzeichen",
        ticket_description=(
            "Kennzeichen SK-334AB, Schwarzenbergplatz Wien. Kamera erkennt "
            "mein Kennzeichen nicht und Schranke bleibt zu. Musste durch "
            "Sprechanlage anrufen. Was läuft falsch?"
        ),
        expected_skills={"bmove_user_lookup", "skidata_session_lookup", "graylog_search"},
        expected_phrases=["lpr", "foreign", "ausländisch", "format", "intercom", "sprechanlage", "blocked"],
        story="Slovak plate format not recognised by LPR",
    ),
    PlateCase(
        plate="I-AM442RR",
        ticket_summary="Richiesta fattura mensile",
        ticket_description=(
            "Targa I-AM442RR, Parcheggi Italia SRL, vorrei la fattura "
            "mensile per tutte le sessioni di parcheggio negli ultimi 7 giorni "
            "a Bologna. Tre sessioni mi risultano."
        ),
        expected_skills={"bmove_user_lookup", "skidata_session_lookup", "datatrans_transaction", "graylog_search"},
        expected_phrases=["3", "tre", "three", "fattura", "invoice", "rechnung", "b2b", "parcheggi italia"],
        story="B2B partner wants monthly invoice; 3 settled sessions",
    ),
    PlateCase(
        plate="W-88211C",
        ticket_summary="Rückerstattung-Anfrage",
        ticket_description=(
            "Kennzeichen W-88211C, am 25. Mai wurden mir 4,50 EUR für die "
            "Garage Millennium City berechnet. Ich bitte um Rückerstattung."
        ),
        expected_skills={"bmove_user_lookup", "datatrans_transaction", "graylog_search"},
        expected_phrases=["refund", "rückerstattung", "already", "bereits", "refunded"],
        story="Refund was already processed 3 days ago",
    ),
    PlateCase(
        plate="ZG-9988-CD",
        ticket_summary="Dvije naplate u isto vrijeme",
        ticket_description=(
            "Imam tri vozila u Bmove računu (ZG-9988-CD, ZG-9988-CE, "
            "ZG-1122-FF). Danas su mi 2 SMS karte odjednom kupljene. "
            "Zašto?"
        ),
        expected_skills={"bmove_user_lookup", "parkis_lookup", "graylog_search"},
        expected_phrases=["2", "two", "dvije", "fleet", "9988", "1122", "vozila", "vehicles"],
        story="Fleet user — 2 concurrent SMS purchases for 2 different plates",
    ),
    PlateCase(
        plate="ZG-1122-FF",
        ticket_summary="Zašto mi je naplaćeno parkiranje",
        ticket_description=(
            "Tablica ZG-1122-FF, danas zona 2 Zagreb, naplata 0.80 EUR. "
            "Imam li za to potvrdu?"
        ),
        expected_skills={"bmove_user_lookup", "parkis_lookup", "graylog_search"},
        expected_phrases=["0,80", "0.80", "zone 2", "active", "confirmed", "potvrđen", "vehicles"],
        story="Sibling plate of fleet user — same account",
    ),
    PlateCase(
        plate="DE-MH-5521",
        ticket_summary="SMS-Zahlung in Zagreb nicht möglich",
        ticket_description=(
            "Kennzeichen DE-MH-5521, war heute in Zagreb Zone 1. SMS ging "
            "nicht durch, habe schliesslich per App bezahlt aber wohl "
            "verspätet. Strafe?"
        ),
        expected_skills={"bmove_user_lookup", "parkis_lookup", "graylog_search"},
        expected_phrases=["foreign", "ausländisch", "sms", "app", "expired", "abgelaufen", "verspätet"],
        story="German plate in Zagreb — SMS failed, app payment late",
    ),
    PlateCase(
        plate="W-44556D",
        ticket_summary="Mehrere offene Forderungen",
        ticket_description=(
            "Kennzeichen W-44556D. Habe mehrere offene Beträge, weiß "
            "nicht woher. Letzte Aktivität war im April."
        ),
        expected_skills={"bmove_user_lookup", "skidata_session_lookup", "datatrans_transaction", "graylog_search"},
        expected_phrases=["3", "drei", "expired", "abgelaufen", "34,20", "34.20", "card", "karte"],
        story="3 months of debt totalling 34.20 — card EXPIRED",
    ),
    PlateCase(
        plate="HR-ZD-442",
        ticket_summary="Krivu zonu sam kupio",
        ticket_description=(
            "Tablica HR-ZD-442, Zadar danas. Kupio sam zonu 3 ali "
            "stvarno sam parkirao u zoni 1. Mogu li dobiti storno?"
        ),
        expected_skills={"parkis_lookup", "graylog_search"},
        expected_phrases=["zone", "zona", "3", "1", "gps", "mismatch", "storno"],
        story="Bought Zone 3, GPS shows Zone 1",
    ),
    PlateCase(
        plate="W-77123E",
        ticket_summary="Schranke öffnet sich nicht automatisch",
        ticket_description=(
            "Kennzeichen W-77123E. Ich habe Bmove und dachte Schranke "
            "öffnet automatisch. Aber Schwarzenbergplatz erkennt mich "
            "nicht. Was läuft falsch?"
        ),
        expected_skills={"bmove_user_lookup"},
        expected_phrases=["ticketless", "disabled", "deaktiviert", "not enabled", "aktivieren", "activate"],
        story="Ticketless flag DISABLED on account",
    ),
    PlateCase(
        plate="ZG-5555-MN",
        ticket_summary="Nije mi došla SMS potvrda",
        ticket_description=(
            "Tablica ZG-5555-MN, Zagreb zona 2 jutros, platio sam SMS "
            "0.80 EUR ali nisam dobio potvrdu nazad. Je li prošlo?"
        ),
        expected_skills={"bmove_user_lookup", "parkis_lookup", "graylog_search"},
        expected_phrases=["0,80", "0.80", "confirmed", "potvrđen", "active", "received", "primljen"],
        story="Everything OK, customer didn't get SMS receipt",
    ),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


@dataclass
class CaseResult:
    plate: str
    story: str
    expected_skills: set[str] = field(default_factory=set)
    called_skills: set[str] = field(default_factory=set)
    skills_with_data: set[str] = field(default_factory=set)
    skills_called_ok: bool = False
    skills_returned_data_ok: bool = False
    comment_grounded: bool = False
    matched_phrases: list[str] = field(default_factory=list)
    comment_excerpt: str = ""
    planner_status: str = ""
    iterations: int = 0
    elapsed_s: float = 0.0
    error: str | None = None


def _load_test_playbook():
    return load_playbook(
        _ROOT / "data/playbooks/end_user/integrations/parking-fine-received-despite-valid-payment.md"
    )


def _data_is_populated(skill_name: str, data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    if data.get("found") is True:
        return True
    if data.get("total_results", 0) > 0:
        return True
    if data.get("user") is not None or data.get("transaction") is not None or data.get("session") is not None:
        return True
    return False


def run_one(case: PlateCase) -> CaseResult:
    ticket_id = f"TEST-{case.plate.replace('-', '_')}"
    res = CaseResult(plate=case.plate, story=case.story, expected_skills=set(case.expected_skills))

    # Clean state
    pending_actions.clear_for_ticket(ticket_id)

    ticket = {
        "key": ticket_id,
        "summary": case.ticket_summary,
        "description": case.ticket_description,
        "labels": [],
    }
    playbook = _load_test_playbook()
    agent_config.set_mode("assisted")

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

    # Inspect audit history filtered to this run
    history = [r for r in agent_audit.list_for_ticket(ticket_id) if r.decided_at >= started_at_iso]
    res.called_skills = {h.skill_name for h in history if h.outcome == "auto"}
    res.skills_with_data = {
        h.skill_name
        for h in history
        if h.outcome == "auto" and h.ok and _data_is_populated(h.skill_name, h.result_data)
    }

    # Verdicts
    res.skills_called_ok = case.expected_skills.issubset(res.called_skills)
    res.skills_returned_data_ok = case.expected_skills.issubset(res.skills_with_data)

    # Pull the proposed public-comment body from the paused tool_use
    pending = pending_actions.list_for_ticket(ticket_id)
    comment_body = ""
    for pa in pending:
        if pa.skill_name == "jira_add_public_comment":
            comment_body = str(pa.skill_input.get("body", "")) or ""
            break
    res.comment_excerpt = comment_body[:240].strip()
    if comment_body:
        cl = comment_body.lower()
        res.matched_phrases = [p for p in case.expected_phrases if p.lower() in cl]
        res.comment_grounded = len(res.matched_phrases) > 0

    # Cleanup
    pending_actions.clear_for_ticket(ticket_id)
    return res


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _verdict_glyph(ok: bool) -> str:
    return "✓" if ok else "✗"


def print_summary(results: list[CaseResult]) -> None:
    print()
    print("=" * 120)
    print(
        f"{'PLATE':14} {'CALLED':4} {'DATA':4} {'CITED':5} {'STATUS':18} {'ITERS':5} {'ELAPSED':8}  STORY"
    )
    print("-" * 120)
    for r in results:
        print(
            f"{r.plate:14} "
            f"{_verdict_glyph(r.skills_called_ok):>4} "
            f"{_verdict_glyph(r.skills_returned_data_ok):>4} "
            f"{_verdict_glyph(r.comment_grounded):>5} "
            f"{r.planner_status:18} "
            f"{r.iterations:>5} "
            f"{r.elapsed_s:>7.1f}s  "
            f"{r.story[:60]}"
        )
    print("-" * 120)
    total = len(results)
    called_ok = sum(1 for r in results if r.skills_called_ok)
    data_ok = sum(1 for r in results if r.skills_returned_data_ok)
    cited_ok = sum(1 for r in results if r.comment_grounded)
    print(
        f"TOTAL · skills called: {called_ok}/{total} · "
        f"data returned: {data_ok}/{total} · comment cited: {cited_ok}/{total}"
    )
    print("=" * 120)

    # Failure detail
    failed = [r for r in results if not (r.skills_called_ok and r.skills_returned_data_ok and r.comment_grounded)]
    if failed:
        print()
        print("Cases not fully passing:")
        for r in failed:
            print(f"\n  [{r.plate}] {r.story}")
            print(f"    expected skills    : {sorted(r.expected_skills)}")
            print(f"    actually called    : {sorted(r.called_skills)}")
            missing = r.expected_skills - r.called_skills
            if missing:
                print(f"    MISSING            : {sorted(missing)}")
            empty = r.called_skills - r.skills_with_data
            if empty:
                print(f"    returned empty     : {sorted(empty)}")
            print(f"    grounded           : {r.comment_grounded}")
            print(f"    matched phrases    : {r.matched_phrases}")
            print(f"    comment excerpt    : {r.comment_excerpt!r}")
            if r.error:
                print(f"    ERROR              : {r.error}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plates",
        nargs="*",
        help="Subset of plates to run (default: all 15). Useful for cost-controlled debug.",
    )
    args = parser.parse_args()

    cases = CASES
    if args.plates:
        wanted = {p.upper() for p in args.plates}
        cases = [c for c in CASES if c.plate.upper() in wanted]
        if not cases:
            print(f"No matching plates among {wanted}. Available: {[c.plate for c in CASES]}")
            return 2

    print(f"Running {len(cases)} plates against the planner (assisted mode).")
    print("Each plate triggers one real planner loop (~$0.05–0.15 Claude tokens).")
    print()

    results: list[CaseResult] = []
    for i, case in enumerate(cases, 1):
        sys.stdout.write(f"[{i:2}/{len(cases)}] {case.plate:14}  {case.story[:50]:50}  … ")
        sys.stdout.flush()
        res = run_one(case)
        results.append(res)
        verdict = (
            "✓"
            if res.skills_called_ok and res.skills_returned_data_ok and res.comment_grounded
            else "✗"
        )
        sys.stdout.write(f"{verdict}  ({res.elapsed_s:.1f}s, iter {res.iterations})\n")
        sys.stdout.flush()

    print_summary(results)

    # Reset mode to shadow so subsequent demo work doesn't surprise the operator.
    agent_config.set_mode("shadow")

    # Exit code: zero iff every case passes all three checks.
    all_ok = all(
        r.skills_called_ok and r.skills_returned_data_ok and r.comment_grounded
        for r in results
    )
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
