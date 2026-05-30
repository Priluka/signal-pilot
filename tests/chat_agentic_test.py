"""Agentic chat end-to-end coverage — 30 tests across three buckets.

Hits ``POST /chat/agentic`` on a running backend (default
``http://localhost:8000``), parses the SSE stream, captures skill
calls + the final answer, and asserts:

  1. **Skills fired iff expected** — plate-bearing questions must
     trigger lookups, generic how-to questions must not.
  2. **Answer is grounded** — for plate tests, at least one expected
     phrase (amount, status word, plate, session id) appears in the
     final body. For "should not hallucinate" tests, the absence of
     fabricated phrases is the grounding check.
  3. **Language match** — the response stays in the language the
     operator wrote in. Mixed-language inputs accept any one match.

Buckets:

  • 15 plate-lookup tests — one per mock plate in
    ``tests/mock_skills_grounding.CASES``.
  • 10 edge cases — empty input, just-emoji, lowercase plate, three
    plates in one turn, plate buried in the middle of long prose,
    mixed-script, etc.
  •  5 knowledge tests — generic how-to questions that must answer
    from playbook prose alone (no skills).

Sequential execution. Each test takes ~10-30s of Anthropic latency.
Total wall time ~5-15 min. Cost on Sonnet 4.6 ≈ $1.50 for the full
sweep.

Run from project root:

    .venv/bin/python tests/chat_agentic_test.py
    .venv/bin/python tests/chat_agentic_test.py --backend http://localhost:8000
    .venv/bin/python tests/chat_agentic_test.py --names plate-W-55123K edge-empty
    .venv/bin/python tests/chat_agentic_test.py --bucket plate    # only plate tests
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / ".env")

from core.retrieval import detect_language  # noqa: E402


# ---------------------------------------------------------------------------
# Test specs
# ---------------------------------------------------------------------------


@dataclass
class TestCase:
    name: str
    bucket: str  # 'plate' | 'edge' | 'knowledge'
    question: str
    expects_skills: bool
    expected_phrases: list[str] = field(default_factory=list)
    # ISO 639-1 code. None disables the check (mixed-language /
    # emoji-only / empty cases). Single string = strict; list = any
    # one match.
    expected_language: str | list[str] | None = None
    story: str = ""
    # HTTP status the request should return. 422 for empty body.
    expects_http_status: int = 200
    # Phrases that the answer must NOT contain (hallucination guard).
    # E.g. data from OTHER plates must never leak.
    forbidden_phrases: list[str] = field(default_factory=list)


# --- 15 plate-lookup tests --------------------------------------------------
# One per mock plate. expected_phrases are short, language-agnostic
# substrings tied to data the lookups return for that plate.

PLATE_CASES: list[TestCase] = [
    TestCase(
        name="plate-W-55123K",
        bucket="plate",
        question="Provjeri W-55123K — kupac kaže da je dvaput naplaćen.",
        expects_skills=True,
        expected_phrases=["4,50", "4.50", "settled", "sess-88421", "einmal", "only", "jedna", "jednom"],
        expected_language="hr",
        story="Austrian double-charge check",
    ),
    TestCase(
        name="plate-W-38702T",
        bucket="plate",
        question="W-38702T — Schwarzenbergplatz. Hat die Schranke nicht geöffnet, ist die Sitzung noch offen?",
        expects_skills=True,
        expected_phrases=["open", "offen", "schranke", "schwarzenbergplatz", "manual", "manuell", "lpr"],
        expected_language="de",
        story="Austrian stuck session at exit",
    ),
    TestCase(
        name="plate-ZG-1234-AB",
        bucket="plate",
        question="Tablica ZG-1234-AB, zona 2 Zagreb, SMS plaćanje 0.80 EUR — je li prošlo?",
        expects_skills=True,
        expected_phrases=["0,80", "0.80", "zone 2", "zona 2", "active", "primljen", "potvrđen", "confirmed", "sms"],
        expected_language="hr",
        story="Croatian SMS payment confirmed",
    ),
    TestCase(
        name="plate-ZG-7777-XY",
        bucket="plate",
        question="ZG-7777-XY — kartica greška, ima li korisnik dugova?",
        expects_skills=True,
        expected_phrases=["expired", "istekla", "abgelaufen", "12,40", "12.40", "card", "kartica"],
        expected_language="hr",
        story="Expired card with 12.40 outstanding",
    ),
    TestCase(
        name="plate-W-12345B",
        bucket="plate",
        question="W-12345B — kupac kaže da je samo prošao kroz Kaptol Center a naplaćen mu je iznos.",
        expects_skills=True,
        expected_phrases=["2,50", "2.50", "kaptol", "5 minuten", "5 minutes", "minimum", "drove through", "prošao"],
        expected_language="hr",
        story="Drove through garage, minimum tariff applied",
    ),
    TestCase(
        name="plate-SK-334AB",
        bucket="plate",
        question="SK-334AB — kamera nije prepoznala plate na Schwarzenbergplatz. Što reći kupcu?",
        expects_skills=True,
        expected_phrases=["lpr", "foreign", "ausländisch", "format", "intercom", "sprechanlage", "slovak", "slovenski"],
        expected_language="hr",
        story="Slovak plate not recognised by LPR",
    ),
    TestCase(
        name="plate-I-AM442RR",
        bucket="plate",
        question="Targa I-AM442RR — Parcheggi Italia richiede fattura mensile, quante sessioni hanno?",
        expects_skills=True,
        expected_phrases=["3", "tre", "three", "fattura", "invoice", "b2b", "parcheggi italia"],
        expected_language="it",
        story="Italian B2B monthly invoice, 3 settled sessions",
    ),
    TestCase(
        name="plate-W-88211C",
        bucket="plate",
        question="W-88211C — Rückerstattungsanfrage für 4.50 EUR vom 25. Mai. Status?",
        expects_skills=True,
        expected_phrases=["refund", "rückerstattung", "already", "bereits", "refunded", "processed"],
        expected_language="de",
        story="Refund already processed",
    ),
    TestCase(
        name="plate-ZG-9988-CD",
        bucket="plate",
        question="Korisnik ZG-9988-CD se žali na dvije naplate. Što piše u sustavu?",
        expects_skills=True,
        expected_phrases=["2", "two", "dvije", "fleet", "9988", "1122", "vozila", "vehicles"],
        expected_language="hr",
        story="Fleet user with 2 concurrent SMS purchases",
    ),
    TestCase(
        name="plate-ZG-1122-FF",
        bucket="plate",
        question="ZG-1122-FF — operator pita za potvrdu plaćanja zone 2 Zagreb.",
        expects_skills=True,
        expected_phrases=["0,80", "0.80", "zone 2", "zona 2", "active", "potvrđen", "confirmed", "fleet"],
        expected_language="hr",
        story="Sibling plate of fleet user, zone 2 payment",
    ),
    TestCase(
        name="plate-DE-MH-5521",
        bucket="plate",
        question="DE-MH-5521 — Kunde versuchte SMS Parking in Zagreb, schließlich App-Zahlung. Strafe?",
        expects_skills=True,
        expected_phrases=["foreign", "ausländisch", "sms", "app", "expired", "abgelaufen", "verspätet", "germ"],
        expected_language="de",
        story="German plate in Zagreb, SMS failed",
    ),
    TestCase(
        name="plate-W-44556D",
        bucket="plate",
        question="W-44556D — više otvorenih dugova. Koliko ukupno i zašto?",
        expects_skills=True,
        expected_phrases=["3", "drei", "expired", "abgelaufen", "34,20", "34.20", "card", "karte", "kartica"],
        expected_language="hr",
        story="3 months of debt, card expired",
    ),
    TestCase(
        name="plate-HR-ZD-442",
        bucket="plate",
        question="HR-ZD-442 — kupac kaže da je kupio krivu zonu u Zadru. Storno?",
        expects_skills=True,
        expected_phrases=["zone", "zona", "3", "1", "gps", "mismatch", "storno", "wrong"],
        expected_language="hr",
        story="Zone 3 bought, GPS shows zone 1",
    ),
    TestCase(
        name="plate-W-77123E",
        bucket="plate",
        question="W-77123E — kupac se žali da mu ticketless ne radi na Schwarzenbergplatz.",
        expects_skills=True,
        expected_phrases=["ticketless", "disabled", "deaktiviert", "not enabled", "aktivieren", "activate"],
        expected_language="hr",
        story="Ticketless flag disabled on account",
    ),
    TestCase(
        name="plate-ZG-5555-MN",
        bucket="plate",
        question="ZG-5555-MN — kupac kaže da nije dobio SMS potvrdu. Zona 2 Zagreb jutros.",
        expects_skills=True,
        expected_phrases=["0,80", "0.80", "confirmed", "potvrđen", "active", "received", "primljen"],
        expected_language="hr",
        story="SMS payment confirmed, receipt not delivered",
    ),
]


# --- 10 edge cases ----------------------------------------------------------

EDGE_CASES: list[TestCase] = [
    TestCase(
        name="edge-just-plate",
        bucket="edge",
        question="W-55123K",
        expects_skills=True,
        expected_phrases=["W-55123K", "settled", "4,50", "found", "more info", "weitere"],
        expected_language=None,
        story="Just a plate, no context — agent must look it up and report",
    ),
    TestCase(
        name="edge-two-plates",
        bucket="edge",
        question="Usporedi W-55123K i W-38702T — koji ima problem?",
        expects_skills=True,
        expected_phrases=["W-55123K", "W-38702T", "schranke", "settled", "4,50", "open", "offen"],
        expected_language="hr",
        story="Two plates in one query",
    ),
    TestCase(
        name="edge-three-plates",
        bucket="edge",
        question="Provjeri ZG-9988-CD, ZG-1122-FF i ZG-5555-MN — sve su povezane?",
        expects_skills=True,
        expected_phrases=["ZG-9988", "ZG-1122", "ZG-5555", "fleet", "vozila"],
        expected_language="hr",
        story="Three plates — agent should handle parallel lookups",
    ),
    TestCase(
        name="edge-plate-buried",
        bucket="edge",
        question=(
            "Jučer me nazvao korisnik s tablicom W-44556D i žalio se na dug, "
            "rekao je nešto o isteku kartice ali nije bio siguran. Možeš provjeriti?"
        ),
        expects_skills=True,
        expected_phrases=["W-44556D", "expired", "abgelaufen", "34,20", "card", "drei", "3 mjeseca"],
        expected_language="hr",
        story="Plate buried in middle of a longer narrative sentence",
    ),
    TestCase(
        name="edge-lowercase-no-dash",
        bucket="edge",
        question="provjeri w55123k — što kaže sustav?",
        # Original test premise (regex case-sensitive → no skills →
        # agent must not fabricate) was wrong: the router upper-cases
        # the question before applying the regex, so "w55123k"
        # matches as "W55123K". The agent then normalises the token to
        # the canonical W-55123K, calls the read skills, and surfaces
        # real data. That's correct, robust behaviour — graceful
        # typo handling rather than fabrication resistance. Test
        # expectations updated accordingly.
        expects_skills=True,
        expected_phrases=["W-55123K", "settled", "sess-88421", "4,50", "found"],
        expected_language="hr",
        story="Lowercase typo — agent normalises and looks up real data",
    ),
    TestCase(
        name="edge-cyrillic-mixed",
        bucket="edge",
        question="Проверьте W-55123K — что в системе?",
        expects_skills=True,
        expected_phrases=["W-55123K", "settled", "4,50", "sess-88421"],
        expected_language=None,  # mixed-script — don't enforce
        story="Cyrillic preamble + Latin plate — regex matches the plate token",
    ),
    TestCase(
        name="edge-mixed-langs",
        bucket="edge",
        question="Check W-38702T, session je stuck. Was sagt das System?",
        expects_skills=True,
        expected_phrases=["W-38702T", "schranke", "open", "offen", "stuck"],
        expected_language=None,
        story="EN+HR+DE in one sentence — plate triggers lookup regardless",
    ),
    TestCase(
        name="edge-empty",
        bucket="edge",
        question="",
        expects_skills=False,
        expected_phrases=[],
        expected_language=None,
        story="Empty question — backend should reject with 422",
        expects_http_status=422,
    ),
    TestCase(
        name="edge-emoji-only",
        bucket="edge",
        question="🚗💰❓",
        expects_skills=False,
        expected_phrases=[],
        forbidden_phrases=["sess-88421", "DT-2026", "4,50", "settled"],
        expected_language=None,
        story="Just emoji — no plate, agent must not invent data",
    ),
    TestCase(
        name="edge-long-prose-trailing-plate",
        bucket="edge",
        question=(
            "Imam dosta dugačko pitanje za tebe. U zadnjih par dana se "
            "kontaktiralo nekoliko korisnika s različitim problemima — "
            "neki su se žalili na sporo procesuiranje refunda, drugi su "
            "imali probleme s SMS plaćanjem u Zagrebu, treći su tvrdili "
            "da im je kartica blokirana iako su je upravo dodali u "
            "aplikaciju. Općenito gledano, vidim trend povećanja "
            "tickets-a u zadnjem tjednu, posebno za garaže u Beču. "
            "Operativno, najveći utjecaj smo osjetili na helpdesk-u jer "
            "su pozivi trajali dulje nego inače. Pa eto, da skratim "
            "priču, glavno pitanje je sljedeće — jedan kupac me sad "
            "kontaktirao i tvrdi da su mu naplaćena dva iznosa od 4,50 "
            "EUR za parkiranje u garaži Millennium City u Beču, datum "
            "27. svibnja. Tablica vozila je W-55123K. Možeš li mi reći "
            "što sustav pokazuje za tu transakciju?"
        ),
        expects_skills=True,
        expected_phrases=["W-55123K", "4,50", "settled", "sess-88421", "millennium"],
        expected_language="hr",
        story="Long narrative with the actual question + plate at the very end",
    ),
]


# --- 5 knowledge tests (no skills should fire) ------------------------------

KNOWLEDGE_CASES: list[TestCase] = [
    TestCase(
        name="knowledge-stuck-session-hr",
        bucket="knowledge",
        question="Kako riješiti stuck session?",
        expects_skills=False,
        expected_phrases=[],
        expected_language="hr",
        story="Generic how-to in Croatian, no plate — playbook prose only",
    ),
    TestCase(
        name="knowledge-refund-policy-en",
        bucket="knowledge",
        question="What is the refund policy?",
        expects_skills=False,
        expected_phrases=[],
        expected_language="en",
        story="Generic refund policy question in English",
    ),
    TestCase(
        name="knowledge-b2b-invoice-hr",
        bucket="knowledge",
        question="Koji su koraci za B2B invoice?",
        expects_skills=False,
        expected_phrases=[],
        expected_language="hr",
        story="B2B invoice steps — playbook prose",
    ),
    TestCase(
        name="knowledge-preauth-vs-settle-en",
        bucket="knowledge",
        question="Explain pre-authorization vs settlement.",
        expects_skills=False,
        expected_phrases=[],
        expected_language="en",
        story="Domain explainer in English",
    ),
    TestCase(
        name="knowledge-refund-duration-hr",
        bucket="knowledge",
        question="Koliko traje obrada refunda?",
        expects_skills=False,
        expected_phrases=[],
        expected_language="hr",
        story="Refund duration question, no plate",
    ),
]


ALL_CASES: list[TestCase] = [*PLATE_CASES, *EDGE_CASES, *KNOWLEDGE_CASES]


# ---------------------------------------------------------------------------
# Result capture
# ---------------------------------------------------------------------------


@dataclass
class TestResult:
    case: TestCase
    skills_called: list[str] = field(default_factory=list)
    answer: str = ""
    detected_language: str | None = None
    elapsed_s: float = 0.0
    http_status: int = 0
    error: str | None = None
    # Computed in finalize()
    skills_match: bool = False
    grounded: bool = False
    language_match: bool = False
    hallucinated: bool = False
    verdict: str = ""

    def finalize(self) -> None:
        # 1. Skills assertion: expected boolean must match actual.
        actually_used = len(self.skills_called) > 0
        self.skills_match = actually_used == self.case.expects_skills

        # 2. Grounded check: at least one expected phrase appears in the
        #    answer (case-insensitive substring). Empty list means N/A.
        body = (self.answer or "").lower()
        if not self.case.expected_phrases:
            self.grounded = True  # nothing to ground against
        else:
            self.grounded = any(
                p.lower() in body for p in self.case.expected_phrases
            )

        # 3. Hallucination check: forbidden phrases must NOT appear.
        self.hallucinated = any(
            p.lower() in body for p in self.case.forbidden_phrases
        )

        # 4. Language match: detect once; allow list-of-acceptable.
        if not self.answer.strip():
            self.detected_language = None
        else:
            self.detected_language = detect_language(self.answer)
        if self.case.expected_language is None:
            self.language_match = True
        elif isinstance(self.case.expected_language, list):
            self.language_match = self.detected_language in self.case.expected_language
        else:
            self.language_match = self.detected_language == self.case.expected_language

        # Verdict precedence: HTTP mismatch > crash > skills wrong >
        # hallucinated > not grounded > wrong language > PASS.
        if self.http_status != self.case.expects_http_status:
            self.verdict = "HTTP"
        elif self.error and self.http_status == 200:
            self.verdict = "CRASH"
        elif not self.skills_match:
            self.verdict = "FAIL"
        elif self.hallucinated:
            self.verdict = "HALLUC"
        elif not self.grounded:
            self.verdict = "UNGROUND"
        elif not self.language_match:
            self.verdict = "LANG"
        else:
            self.verdict = "PASS"


# ---------------------------------------------------------------------------
# HTTP runner — POST /chat/agentic, parse SSE stream
# ---------------------------------------------------------------------------


def _parse_sse_blocks(line_iter) -> Any:
    """Yield (event_name, data_dict) tuples from a line iterator."""
    event_name = "message"
    data_buf: list[str] = []
    for raw in line_iter:
        line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        line = line.rstrip("\n").rstrip("\r")
        if not line:
            if data_buf:
                try:
                    payload = json.loads("\n".join(data_buf))
                except json.JSONDecodeError:
                    payload = {"raw": "\n".join(data_buf)}
                yield event_name, payload
            event_name = "message"
            data_buf = []
            continue
        if line.startswith("event:"):
            event_name = line[len("event:"):].strip()
        elif line.startswith("data:"):
            data_buf.append(line[len("data:"):].strip())
    if data_buf:
        try:
            payload = json.loads("\n".join(data_buf))
        except json.JSONDecodeError:
            payload = {"raw": "\n".join(data_buf)}
        yield event_name, payload


def run_one(case: TestCase, *, backend: str, top_k: int = 3) -> TestResult:
    res = TestResult(case=case)
    started = time.time()
    try:
        resp = requests.post(
            f"{backend}/chat/agentic",
            json={"question": case.question, "top_k": top_k},
            stream=True,
            timeout=180,
        )
        res.http_status = resp.status_code
        if resp.status_code != 200:
            # Read body for diagnostic but don't try to parse SSE.
            res.error = (resp.text or "")[:200]
            res.elapsed_s = time.time() - started
            res.finalize()
            return res
        for event_name, payload in _parse_sse_blocks(resp.iter_lines()):
            if event_name == "skill_executed":
                # Only count completed calls so a stuck executing row
                # doesn't pad the result.
                skill = payload.get("skill")
                if skill:
                    res.skills_called.append(str(skill))
            elif event_name == "delta":
                res.answer += str(payload.get("text", ""))
            elif event_name == "done":
                # Done event carries the canonical full answer — use it
                # to override delta accumulation in case of any rounding.
                final = payload.get("answer")
                if isinstance(final, str) and final:
                    res.answer = final
                break
            elif event_name == "error":
                res.error = str(payload.get("message", "stream error"))
                break
    except Exception as exc:  # noqa: BLE001
        res.error = f"{type(exc).__name__}: {exc}"
    res.elapsed_s = time.time() - started
    res.finalize()
    return res


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


_VERDICT_GLYPH = {
    "PASS": "✓",
    "FAIL": "✗",
    "DRIFT": "~",
    "UNGROUND": "~",
    "LANG": "~",
    "HALLUC": "!",
    "CRASH": "!",
    "HTTP": "!",
}


def _column(label: str, ok: bool, detail: str = "") -> str:
    """Compact glyph+detail cell. Falls back to '-' for N/A checks."""
    if detail == "n/a":
        return "n/a    "
    g = "✓" if ok else "✗"
    return f"{g} {detail}".ljust(7) if detail else f"{g}      "


def print_table(results: list[TestResult]) -> None:
    print()
    print("=" * 132)
    print(
        f"{'TEST':30} {'BUCKET':9} {'SKILLS':14} {'GROUNDED':10} "
        f"{'LANG':6} {'TIME':6}  STORY"
    )
    print("-" * 132)
    for r in results:
        c = r.case
        # Skills column: show count + expected
        if c.expects_skills:
            sk_detail = f"{len(r.skills_called)} called" if r.skills_called else "0 — MISS"
        else:
            sk_detail = "0 (none)" if not r.skills_called else f"{len(r.skills_called)} — STRAY"
        sk_glyph = "✓" if r.skills_match else "✗"
        if c.expected_phrases:
            gr_detail = "yes" if r.grounded else "no"
            gr_glyph = "✓" if r.grounded else "✗"
        else:
            gr_detail = "n/a"
            gr_glyph = "·"
        if c.expected_language is None:
            lg_detail = r.detected_language or "?"
            lg_glyph = "·"
        else:
            lg_detail = r.detected_language or "?"
            lg_glyph = "✓" if r.language_match else "✗"
        v = r.verdict
        verdict_str = f"{_VERDICT_GLYPH.get(v, '?')} {v}"
        print(
            f"{c.name:30} {c.bucket:9} {sk_glyph} {sk_detail:12} "
            f"{gr_glyph} {gr_detail:7} {lg_glyph} {lg_detail:3} "
            f"{r.elapsed_s:5.1f}s  {verdict_str:10} {c.story[:50]}"
        )
    print("-" * 132)

    # Summary
    by_verdict: dict[str, int] = {}
    for r in results:
        by_verdict[r.verdict] = by_verdict.get(r.verdict, 0) + 1
    parts = [
        f"{_VERDICT_GLYPH.get(k, '?')} {k}={v}"
        for k, v in sorted(by_verdict.items())
    ]
    print(f"TOTAL  {len(results)} tests  ·  {'  '.join(parts)}")

    # Detail section: anything not PASS
    interesting = [r for r in results if r.verdict != "PASS"]
    if interesting:
        print()
        print("DETAIL — non-pass tests")
        print("-" * 132)
        for r in interesting:
            print(f"\n  [{r.verdict}] {r.case.name}")
            print(f"    question  : {r.case.question[:120]}")
            print(f"    skills    : {r.skills_called}  (expected_skills={r.case.expects_skills})")
            if r.case.expected_phrases:
                hit = [p for p in r.case.expected_phrases if p.lower() in r.answer.lower()]
                miss = [p for p in r.case.expected_phrases if p.lower() not in r.answer.lower()]
                print(f"    phrases   : hit {len(hit)}/{len(r.case.expected_phrases)}: {hit[:5]}")
                if not r.grounded:
                    print(f"    none of: {miss[:6]}")
            if r.case.forbidden_phrases:
                leaked = [p for p in r.case.forbidden_phrases if p.lower() in r.answer.lower()]
                if leaked:
                    print(f"    LEAKED forbidden phrases: {leaked}")
            if r.case.expected_language is not None:
                print(f"    language  : detected={r.detected_language!r}, expected={r.case.expected_language!r}")
            if r.error:
                print(f"    error     : {r.error[:200]}")
            head = (r.answer or "").strip().replace("\n", " ")[:160]
            print(f"    answer    : {head}…")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="http://localhost:8000")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--names", nargs="+", default=None,
        help="Subset of test names to run (e.g. plate-W-55123K edge-empty)",
    )
    parser.add_argument(
        "--bucket",
        choices=("plate", "edge", "knowledge"),
        default=None,
        help="Only run one bucket",
    )
    args = parser.parse_args()

    cases = ALL_CASES
    if args.bucket:
        cases = [c for c in cases if c.bucket == args.bucket]
    if args.names:
        wanted = set(args.names)
        cases = [c for c in cases if c.name in wanted]
    if not cases:
        print("no matching cases", file=sys.stderr)
        return 1

    # Smoke ping so we fail fast if the backend is down.
    try:
        ping = requests.get(f"{args.backend}/health", timeout=5)
        if ping.status_code != 200:
            print(f"backend /health = {ping.status_code}", file=sys.stderr)
            return 2
    except Exception as exc:  # noqa: BLE001
        print(f"backend unreachable at {args.backend}: {exc}", file=sys.stderr)
        return 2

    print(
        f"Agentic chat sweep · {len(cases)} cases  ·  ~10-30s each  "
        "·  sequential"
    )
    print()
    overall_start = time.time()
    results: list[TestResult] = []
    for i, c in enumerate(cases, 1):
        print(
            f"[{i:2d}/{len(cases)}]  {c.name:30s} ...",
            end=" ", flush=True,
        )
        r = run_one(c, backend=args.backend, top_k=args.top_k)
        results.append(r)
        print(f"{_VERDICT_GLYPH.get(r.verdict,'?')} {r.verdict} ({r.elapsed_s:.1f}s)")

    elapsed = time.time() - overall_start
    print_table(results)
    print(f"\nTotal wall time: {elapsed / 60:.1f} min")
    return 0 if all(r.verdict == "PASS" for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
