"""Multi-turn chat stress suite — 15 scenarios × 3 runs each.

Four buckets exercise the same machinery the operator-facing chat
relies on, each from a different angle:

  Bucket 1 — Context memory (T01-T05)
    Verifies that information introduced in earlier turns (a plate,
    a tool result, an open thread of reasoning) stays in scope as
    the conversation deepens, without the operator having to repeat
    themselves.

  Bucket 2 — Context switching (T06-T08)
    Multiple subjects in one thread, off-topic detours, mid-stream
    corrections. The agent has to pick the right antecedent.

  Bucket 3 — search_playbooks fallback (T09-T11)
    The initial playbook stops being relevant; the agent has to use
    search_playbooks to discover a better one mid-conversation.

  Bucket 4 — Edge cases (T12-T15)
    Empty messages, oversized prompts with the signal buried at the
    end, redundant repeats, emoji-only follow-ups.

Each test = a list of TurnSpec objects (user_text + zero-or-more
per-turn assertions). The driver creates a fresh thread per run, walks
the turns, captures the SSE event stream and final answer text, and
collects pass/fail.

Cost: ~150-200 Anthropic turn calls per full sweep, roughly $5-10 on
Sonnet 4.6. Wall time: ~30-60 min.

Run from project root:

    .venv/bin/python tests/multi_turn_stress.py
    .venv/bin/python tests/multi_turn_stress.py --names T01 T06 T09
    .venv/bin/python tests/multi_turn_stress.py --runs 1   # quick smoke
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))


BACKEND_BASE = "http://127.0.0.1:8000"

# Plates that exist in tests/mock_skills_grounding.py. Using these
# guarantees the mock skills return ``found=true`` payloads so the
# agent has substance to reference in follow-up turns.
PLATE_A = "W-55123K"
PLATE_B = "ZG-1234-AB"
PLATE_C = "W-38702T"
PLATE_D = "W-44556D"


# ---------------------------------------------------------------------------
# HTTP / SSE plumbing
# ---------------------------------------------------------------------------


@dataclass
class TurnOutcome:
    """Everything we capture from one operator → agent turn."""
    turn_id: int
    events: list[dict[str, Any]]
    final_text: str
    duration_s: float


def _backend_reachable() -> bool:
    try:
        with urllib.request.urlopen(
            f"{BACKEND_BASE}/health", timeout=2.0
        ) as resp:
            return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


def _create_thread() -> int:
    req = urllib.request.Request(
        f"{BACKEND_BASE}/chat/threads",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return int(body["id"])


def _stream_turn(thread_id: int, user_text: str) -> TurnOutcome:
    """POST /chat/threads/{id}/turns, parse SSE, return the outcome.
    Blocks until ``done`` or ``error`` is received."""
    start = time.perf_counter()
    body = json.dumps({"user_text": user_text, "top_k": 3}).encode("utf-8")
    req = urllib.request.Request(
        f"{BACKEND_BASE}/chat/threads/{thread_id}/turns",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    events: list[dict[str, Any]] = []
    turn_id = -1
    final_text = ""
    with urllib.request.urlopen(req, timeout=300) as resp:
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
                evt = {"type": evt_type, **payload}
                events.append(evt)
                if evt_type == "turn":
                    turn_id = int(payload["turn"]["id"])
                if evt_type == "delta":
                    final_text += str(payload.get("text") or "")
                if evt_type in ("done", "error"):
                    return TurnOutcome(
                        turn_id=turn_id,
                        events=events,
                        final_text=final_text,
                        duration_s=time.perf_counter() - start,
                    )
    return TurnOutcome(
        turn_id=turn_id,
        events=events,
        final_text=final_text,
        duration_s=time.perf_counter() - start,
    )


# ---------------------------------------------------------------------------
# Assertion helpers — each is a closure returning a callable(TurnOutcome)
# that raises AssertionError on failure.
# ---------------------------------------------------------------------------


def _skill_events(turn: TurnOutcome) -> list[dict[str, Any]]:
    return [
        e for e in turn.events
        if e.get("type") in ("skill_executing", "skill_executed")
    ]


def _skill_params_blob(turn: TurnOutcome) -> str:
    """All skill params concatenated into one upper-cased string for
    substring checks. Cheap and good enough for plate / id presence."""
    parts: list[str] = []
    for ev in _skill_events(turn):
        params = ev.get("params") or {}
        parts.append(json.dumps(params))
    return " ".join(parts).upper()


def _plate_visible(turn: TurnOutcome, plate: str) -> bool:
    p = plate.upper()
    if p in _skill_params_blob(turn):
        return True
    if p in turn.final_text.upper():
        return True
    # Some plates are stored with/without dashes — check both forms.
    p_alt = p.replace("-", "")
    if p_alt in _skill_params_blob(turn).replace("-", ""):
        return True
    if p_alt in turn.final_text.upper().replace("-", ""):
        return True
    return False


def assert_plate_in_context(plate: str) -> Callable[[TurnOutcome], None]:
    """Strong check — the named plate must surface either as a skill
    param or in the answer text. Use for turns where the operator
    explicitly invokes a prior plate."""

    def check(turn: TurnOutcome) -> None:
        if _plate_visible(turn, plate):
            return
        raise AssertionError(
            f"plate {plate} not in turn context. "
            f"answer_head={turn.final_text[:160]!r}"
        )

    return check


# Croatian + English phrasings the agent uses when it RECOGNISES a
# repeat / continuation and answers from prior context without firing
# a fresh skill or echoing the plate string. Used by
# ``assert_plate_in_context_or_continuation`` below.
_CONTINUATION_NEEDLES = (
    "već sam",
    "već provjer",
    "isti podaci",
    "podaci se nisu promijenili",
    "podaci nisu prom",
    "kao gore",
    "kao što sam",
    "kao maloprije",
    "ranije sam",
    "ništa novo",
    "no change",
    "already checked",
    "as i said",
    "same data",
    "no new data",
)


def assert_plate_in_context_or_continuation(
    plate: str,
) -> Callable[[TurnOutcome], None]:
    """Relaxed check used by T14 and similar repeat-question tests.
    A turn passes if EITHER the plate appears in skill params / final
    text (strong evidence of context), OR the agent's text explicitly
    flags the question as a repeat (smart cache — also evidence of
    context, just without re-emitting the plate)."""

    def check(turn: TurnOutcome) -> None:
        if _plate_visible(turn, plate):
            return
        text = turn.final_text.lower()
        for n in _CONTINUATION_NEEDLES:
            if n in text:
                return
        raise AssertionError(
            f"plate {plate} not in context and no continuation marker. "
            f"answer_head={turn.final_text[:200]!r}"
        )

    return check


def assert_does_not_ask_for_plate() -> Callable[[TurnOutcome], None]:
    """Soft check — the agent must not request a plate from the
    operator when prior turns already provide one. Heuristic match
    on common Croatian + English clarification phrasings."""
    needles = [
        "koja je plat",
        "koja je regis",
        "trebam plat",
        "trebam regis",
        "treba mi plat",
        "treba mi regis",
        "daj mi plat",
        "daj mi regis",
        "specify the plate",
        "which plate",
        "need a plate",
        "need the plate",
        "provide the plate",
        "what's the plate",
    ]

    def check(turn: TurnOutcome) -> None:
        text = turn.final_text.lower()
        for n in needles:
            if n in text:
                raise AssertionError(
                    f"agent asked for plate (matched {n!r}). "
                    f"answer_head={turn.final_text[:160]!r}"
                )

    return check


def assert_skill_called(skill_name: str) -> Callable[[TurnOutcome], None]:
    def check(turn: TurnOutcome) -> None:
        for ev in _skill_events(turn):
            if ev.get("skill") == skill_name:
                return
        skills = [ev.get("skill") for ev in _skill_events(turn)]
        raise AssertionError(
            f"expected skill {skill_name!r} not called. fired: {skills}"
        )

    return check


def assert_skill_not_called_with(
    skill_name: str, forbidden: str
) -> Callable[[TurnOutcome], None]:
    """For T08 — after correcting to a new plate, the wrong plate
    must not appear in any subsequent skill invocation."""

    def check(turn: TurnOutcome) -> None:
        for ev in _skill_events(turn):
            if ev.get("skill") != skill_name:
                continue
            params = ev.get("params") or {}
            blob = json.dumps(params).upper()
            if forbidden.upper() in blob:
                raise AssertionError(
                    f"{skill_name} invoked with forbidden value "
                    f"{forbidden!r}: params={params}"
                )

    return check


def assert_no_error_event() -> Callable[[TurnOutcome], None]:
    """The turn finished without the ``error`` SSE event — any crash
    surface (Anthropic 4xx, internal exception) lands here."""

    def check(turn: TurnOutcome) -> None:
        for ev in turn.events:
            if ev.get("type") == "error":
                raise AssertionError(
                    f"error event: {ev.get('message') or ev}"
                )

    return check


def assert_text_min_chars(n: int) -> Callable[[TurnOutcome], None]:
    """The agent produced a substantive reply — at least ``n`` chars
    of streamed text. Catches the case where it silently emits an
    empty turn."""

    def check(turn: TurnOutcome) -> None:
        if len(turn.final_text.strip()) < n:
            raise AssertionError(
                f"answer too short ({len(turn.final_text)} chars < {n}). "
                f"text={turn.final_text!r}"
            )

    return check


def assert_text_contains_any(*needles: str) -> Callable[[TurnOutcome], None]:
    def check(turn: TurnOutcome) -> None:
        text = turn.final_text.upper()
        for n in needles:
            if n.upper() in text:
                return
        raise AssertionError(
            f"none of {needles} found in answer. "
            f"head={turn.final_text[:200]!r}"
        )

    return check


# ---------------------------------------------------------------------------
# Test scaffold
# ---------------------------------------------------------------------------


@dataclass
class TurnSpec:
    user_text: str
    assertions: list[Callable[[TurnOutcome], None]] = field(default_factory=list)
    # Some turns may legitimately fail at the HTTP layer (T12 empty).
    # If allow_http_error is True, a 4xx from the backend is treated
    # as PASS for that turn.
    allow_http_error: bool = False


@dataclass
class TestSpec:
    code: str
    bucket: str
    description: str
    turns: list[TurnSpec]


@dataclass
class RunResult:
    passed: bool
    duration_s: float
    error: str = ""
    crashed: bool = False
    turn_summaries: list[str] = field(default_factory=list)


@dataclass
class TestResult:
    spec: TestSpec
    runs: list[RunResult]


def execute_run(spec: TestSpec) -> RunResult:
    """Execute one full pass of the test (one fresh thread, all turns).
    Returns RunResult with passed/crashed/error captured."""
    start = time.perf_counter()
    try:
        thread_id = _create_thread()
    except Exception as exc:  # noqa: BLE001
        return RunResult(
            passed=False,
            duration_s=time.perf_counter() - start,
            crashed=True,
            error=f"thread create failed: {type(exc).__name__}: {exc}",
        )

    summaries: list[str] = []
    for i, tspec in enumerate(spec.turns, start=1):
        try:
            outcome = _stream_turn(thread_id, tspec.user_text)
        except urllib.error.HTTPError as exc:  # type: ignore[attr-defined]
            if tspec.allow_http_error:
                summaries.append(f"T{i}:http_{exc.code}(expected)")
                continue
            return RunResult(
                passed=False,
                duration_s=time.perf_counter() - start,
                crashed=True,
                error=f"turn {i} HTTP {exc.code}: {exc}",
                turn_summaries=summaries,
            )
        except Exception as exc:  # noqa: BLE001
            return RunResult(
                passed=False,
                duration_s=time.perf_counter() - start,
                crashed=True,
                error=f"turn {i} crash: {type(exc).__name__}: {exc}",
                turn_summaries=summaries,
            )

        skill_names = [ev.get("skill") for ev in _skill_events(outcome)]
        summaries.append(
            f"T{i}:{outcome.duration_s:.1f}s skills={skill_names} "
            f"text_len={len(outcome.final_text)}"
        )
        for asser in tspec.assertions:
            try:
                asser(outcome)
            except AssertionError as exc:
                return RunResult(
                    passed=False,
                    duration_s=time.perf_counter() - start,
                    error=f"turn {i} assertion: {exc}",
                    turn_summaries=summaries,
                )

    return RunResult(
        passed=True,
        duration_s=time.perf_counter() - start,
        turn_summaries=summaries,
    )


# ---------------------------------------------------------------------------
# Test catalogue
# ---------------------------------------------------------------------------


def _build_tests() -> list[TestSpec]:
    tests: list[TestSpec] = []

    # ---- Bucket 1 — Context memory ----

    # T01 — 5-turn drill: plate → details → debts → card → advice.
    tests.append(TestSpec(
        code="T01",
        bucket="ctx-memory",
        description="5-turn drill on a single plate",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[
                    assert_no_error_event(),
                    assert_text_min_chars(20),
                ],
            ),
            TurnSpec(
                user_text="Daj mi više detalja o tom korisniku.",
                assertions=[
                    assert_no_error_event(),
                    assert_does_not_ask_for_plate(),
                ],
            ),
            TurnSpec(
                user_text="Ima li ikakvih dugovanja ili neplaćenih sessiona?",
                assertions=[
                    assert_no_error_event(),
                    assert_does_not_ask_for_plate(),
                ],
            ),
            TurnSpec(
                user_text="Što je s karticom — ima li aktivnu plaćanu metodu?",
                assertions=[
                    assert_no_error_event(),
                    assert_does_not_ask_for_plate(),
                ],
            ),
            TurnSpec(
                user_text="Što mu da predložim kao sljedeći korak?",
                assertions=[
                    assert_no_error_event(),
                    assert_does_not_ask_for_plate(),
                    assert_text_min_chars(40),
                ],
            ),
        ],
    ))

    # T02 — Two plates in turn 1, then disambiguation question.
    tests.append(TestSpec(
        code="T02",
        bucket="ctx-memory",
        description="Two plates then 'which one has the problem'",
        turns=[
            TurnSpec(
                user_text=(
                    f"Provjeri obje plate: {PLATE_A} i {PLATE_B}. "
                    "Daj mi Bmove status za svaku."
                ),
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context(PLATE_A),
                    assert_plate_in_context(PLATE_B),
                ],
            ),
            TurnSpec(
                user_text="Koji od njih ima problem?",
                assertions=[
                    assert_no_error_event(),
                    assert_does_not_ask_for_plate(),
                    # The agent should reference at least one of the
                    # two plates by name when answering the comparison.
                    assert_text_contains_any(PLATE_A, PLATE_B),
                ],
            ),
        ],
    ))

    # T03 — Long-range recall: plate at T1, three unrelated detours,
    # then "go back to that first plate".
    tests.append(TestSpec(
        code="T03",
        bucket="ctx-memory",
        description="Long-range recall after 3 detour turns",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text="Što je GDPR u kontekstu naših podataka?",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text="Koliko ima parkirališta u Hrvatskoj općenito?",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text="Tko je voditelj support tima?",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text=(
                    "Vrati se na onu prvu tablicu s početka razgovora — "
                    "što smo zapravo našli za nju?"
                ),
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context(PLATE_A),
                ],
            ),
        ],
    ))

    # T04 — Agent collects details over multiple turns (operator
    # provides the plate only in turn 2 after a vague turn 1).
    tests.append(TestSpec(
        code="T04",
        bucket="ctx-memory",
        description="Operator drips info; agent must use it once provided",
        turns=[
            TurnSpec(
                user_text=(
                    "Imam korisnika koji se žali da mu se naplaćuje "
                    "parkiranje dva puta. Trebam pomoć."
                ),
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text=f"Plate je {PLATE_A}. Provjeri sve.",
                assertions=[
                    assert_no_error_event(),
                    # Now that the plate is provided, the agent must
                    # actually fire a lookup. Any of the plate-aware
                    # skills counts.
                    assert_text_min_chars(40),
                    assert_plate_in_context(PLATE_A),
                ],
            ),
        ],
    ))

    # T05 — Same plate, 10 follow-up questions. Agent must keep the
    # context across all of them without asking for plate again.
    tests.append(TestSpec(
        code="T05",
        bucket="ctx-memory",
        description="10 follow-ups on the same plate",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context(PLATE_A),
                ],
            ),
            *[
                TurnSpec(
                    user_text=q,
                    assertions=[
                        assert_no_error_event(),
                        assert_does_not_ask_for_plate(),
                    ],
                )
                for q in [
                    "Koji je tip naplate kod ovog korisnika?",
                    "Postoji li otvoren session?",
                    "Kad je zadnji put plaćao?",
                    "Ima li history sporova?",
                    "Koja je metoda plaćanja registrirana?",
                    "Koliko često parkira mjesečno?",
                    "Je li ikad bio blokiran?",
                    "Što kaže Datatrans o zadnjoj transakciji?",
                    "Postoji li Jira ticket otvoren?",
                ]
            ],
        ],
    ))

    # ---- Bucket 2 — Context switching ----

    # T06 — A, B, compare, which has debt.
    tests.append(TestSpec(
        code="T06",
        bucket="ctx-switch",
        description="Two plates introduced separately, then compared",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[assert_no_error_event(),
                            assert_plate_in_context(PLATE_A)],
            ),
            TurnSpec(
                user_text=f"A sad isto za {PLATE_B}.",
                assertions=[assert_no_error_event(),
                            assert_plate_in_context(PLATE_B)],
            ),
            TurnSpec(
                user_text="Usporedi ih — što vidiš?",
                assertions=[
                    assert_no_error_event(),
                    assert_text_contains_any(PLATE_A, PLATE_B),
                ],
            ),
            TurnSpec(
                user_text="Koji od njih ima nekakva dugovanja ili problem?",
                assertions=[
                    assert_no_error_event(),
                    assert_text_contains_any(PLATE_A, PLATE_B),
                ],
            ),
        ],
    ))

    # T07 — Detour into off-topic, then back to plate.
    tests.append(TestSpec(
        code="T07",
        bucket="ctx-switch",
        description="Off-topic detour then 'continue with that plate'",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[assert_no_error_event(),
                            assert_plate_in_context(PLATE_A)],
            ),
            TurnSpec(
                user_text="Inače, što je GDPR ukratko?",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text=(
                    "Ok, vrati se na onu tablicu s početka — "
                    "što smo našli za njega?"
                ),
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context(PLATE_A),
                ],
            ),
        ],
    ))

    # T08 — Operator corrects the plate in turn 2.
    tests.append(TestSpec(
        code="T08",
        bucket="ctx-switch",
        description="Operator corrects plate mid-conversation",
        turns=[
            TurnSpec(
                user_text=f"Provjeri {PLATE_A}.",
                assertions=[assert_no_error_event(),
                            assert_plate_in_context(PLATE_A)],
            ),
            TurnSpec(
                user_text=(
                    f"Čekaj, krivo sam napisao. Mislio sam {PLATE_C}. "
                    "Možeš li umjesto toga provjeriti tu?"
                ),
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context(PLATE_C),
                    # The wrong plate must NOT be re-queried after the
                    # correction. Check each Bmove call's params.
                    assert_skill_not_called_with(
                        "bmove_user_lookup", PLATE_A
                    ),
                ],
            ),
        ],
    ))

    # ---- Bucket 3 — search_playbooks fallback ----

    # T09 — Operator explicitly asks which playbook covers the case.
    tests.append(TestSpec(
        code="T09",
        bucket="search-pb",
        description="Operator asks which playbook applies",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text=(
                    "Koji playbook iz baze pokriva ovakav slučaj? "
                    "Pretraži ih."
                ),
                assertions=[
                    assert_no_error_event(),
                    assert_skill_called("search_playbooks"),
                ],
            ),
        ],
    ))

    # T10 — Turn 1 is one domain; turn 2 jumps to a different domain.
    tests.append(TestSpec(
        code="T10",
        bucket="search-pb",
        description="Cross-domain jump forces search_playbooks",
        turns=[
            TurnSpec(
                user_text=(
                    "Imam pitanje o tome kako rade naplate u "
                    "Bmove sistemu."
                ),
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text=(
                    "Nešto drugo — kako resetirati Android PPC "
                    "terminal? Treba mi taj playbook."
                ),
                assertions=[
                    assert_no_error_event(),
                    assert_skill_called("search_playbooks"),
                ],
            ),
        ],
    ))

    # T11 — Three-turn drift across topics; agent has to relocate.
    tests.append(TestSpec(
        code="T11",
        bucket="search-pb",
        description="Multi-turn drift, agent must relocate playbook",
        turns=[
            TurnSpec(
                user_text="Imam pitanje o Bmove sustavu plaćanja.",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text="Općenito, kako rade refundi?",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text=(
                    "Zapravo, prebaci se — treba mi informacija o "
                    "SKIDATA session lookupu. Pretraži playbook za to."
                ),
                assertions=[
                    assert_no_error_event(),
                    assert_skill_called("search_playbooks"),
                ],
            ),
        ],
    ))

    # ---- Bucket 4 — Edge cases ----

    # T12 — Empty follow-up. Backend has a 422 guard at the request
    # validation layer; we just need to verify graceful rejection.
    tests.append(TestSpec(
        code="T12",
        bucket="edge",
        description="Empty follow-up turn is rejected, no crash",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text="",
                allow_http_error=True,  # backend should 422
                assertions=[],
            ),
        ],
    ))

    # T13 — Very long prompt with the plate near the end.
    long_blob = (
        "Korisnik me kontaktirao preko e-maila jutros s opširnim "
        "opisom problema. Tvrdi da već mjesec dana ima problema s "
        "naplatama, da mu se događa dupla naplata barem dva puta "
        "tjedno, da je već zvao customer support nekoliko puta i "
        "nitko mu nije konkretno odgovorio. Spominje da je "
        "dokumentirao sve transakcije, ima slike s ekrana, ima "
        "PDF račune od banke, ima dopisivanje s nama. Hoće "
        "rješenje, prijeti pravnim postupkom, traži povrat svih "
        "neispravno naplaćenih iznosa. Glavna težina je u tome da "
        "nemamo ujedno svi pristup istom view-u — ja vidim samo "
        "Bmove, kolega iz finansija vidi Datatrans, treći kolega "
        "ima SKIDATA. Trebam triage. "
    )
    long_blob = (long_blob * 4) + f"Plate je {PLATE_A}."
    tests.append(TestSpec(
        code="T13",
        bucket="edge",
        description="Long prompt (1000+ chars) with plate at the tail",
        turns=[
            TurnSpec(
                user_text=long_blob,
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context(PLATE_A),
                ],
            ),
        ],
    ))

    # T14 — Same question three times. Two legitimate behaviours:
    # (a) the agent re-fires the lookup with the same plate, or
    # (b) the agent recognises the repeat and answers from prior
    # context ("već sam to provjerio gore..."). Both prove context
    # carry. Turn 1 uses the strong asserter (no prior context yet);
    # turns 2 and 3 use the relaxed asserter that accepts either path.
    tests.append(TestSpec(
        code="T14",
        bucket="edge",
        description="Same question repeated 3x — no crash, consistent",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[assert_no_error_event(),
                            assert_plate_in_context(PLATE_A)],
            ),
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context_or_continuation(PLATE_A),
                ],
            ),
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[
                    assert_no_error_event(),
                    assert_plate_in_context_or_continuation(PLATE_A),
                ],
            ),
        ],
    ))

    # T15 — Emoji-only follow-up. Agent must respond gracefully.
    tests.append(TestSpec(
        code="T15",
        bucket="edge",
        description="Emoji-only follow-up after plate lookup",
        turns=[
            TurnSpec(
                user_text=f"Provjeri Bmove za {PLATE_A}.",
                assertions=[assert_no_error_event()],
            ),
            TurnSpec(
                user_text="🤔",
                assertions=[
                    assert_no_error_event(),
                    # Some non-empty acknowledgment / clarification.
                    assert_text_min_chars(10),
                ],
            ),
        ],
    ))

    return tests


# ---------------------------------------------------------------------------
# Driver + reporting
# ---------------------------------------------------------------------------


def run_test(spec: TestSpec, runs: int) -> TestResult:
    print(f"\n=== {spec.code} [{spec.bucket}] {spec.description} ===")
    results: list[RunResult] = []
    for r in range(1, runs + 1):
        print(f"  run {r}/{runs}…", end=" ", flush=True)
        result = execute_run(spec)
        results.append(result)
        if result.crashed:
            print(f"CRASH ({result.duration_s:.1f}s) — {result.error}")
        elif result.passed:
            print(f"PASS ({result.duration_s:.1f}s)")
        else:
            print(f"FAIL ({result.duration_s:.1f}s) — {result.error}")
    return TestResult(spec=spec, runs=results)


def print_summary(all_results: list[TestResult]) -> int:
    print("\n" + "=" * 96)
    print("MULTI-TURN STRESS SUMMARY")
    print("=" * 96)
    header = (
        f"| {'Test':4} | {'Bucket':10} | {'Runs':7} | {'Cons':4} | "
        f"{'Description':45} | {'Notes':30} |"
    )
    print(header)
    print("|" + "-" * (len(header) - 2) + "|")

    total_pass_runs = 0
    total_runs = 0
    fully_passing_tests = 0

    for tr in all_results:
        passed = sum(1 for r in tr.runs if r.passed)
        total_runs += len(tr.runs)
        total_pass_runs += passed
        if passed == len(tr.runs):
            fully_passing_tests += 1
            consistency = "100%"
        elif passed == 0:
            consistency = "0%"
        else:
            consistency = f"{passed * 100 // len(tr.runs)}%"
        notes_parts: list[str] = []
        crashed = sum(1 for r in tr.runs if r.crashed)
        if crashed:
            notes_parts.append(f"{crashed} crash")
        if passed < len(tr.runs):
            # First failing error for context
            for r in tr.runs:
                if not r.passed:
                    notes_parts.append(r.error[:50])
                    break
        notes = "; ".join(notes_parts) or "ok"
        print(
            f"| {tr.spec.code:4} | {tr.spec.bucket:10} | "
            f"{passed}/{len(tr.runs):<3}  | {consistency:4} | "
            f"{tr.spec.description[:45]:45} | {notes[:30]:30} |"
        )

    print("=" * 96)
    print(
        f"Totals: {total_pass_runs}/{total_runs} runs passed | "
        f"{fully_passing_tests}/{len(all_results)} tests with 100% consistency"
    )
    return 0 if total_pass_runs == total_runs else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--names",
        nargs="*",
        default=None,
        help="Run only these test codes (e.g. T01 T05)",
    )
    parser.add_argument(
        "--bucket",
        default=None,
        help="Run only this bucket (ctx-memory|ctx-switch|search-pb|edge)",
    )
    parser.add_argument(
        "--runs", type=int, default=3, help="Runs per test (default 3)"
    )
    args = parser.parse_args()

    if not _backend_reachable():
        print(f"ERROR: backend not reachable at {BACKEND_BASE}", file=sys.stderr)
        return 2

    tests = _build_tests()
    if args.names:
        tests = [t for t in tests if t.code in set(args.names)]
    if args.bucket:
        tests = [t for t in tests if t.bucket == args.bucket]
    if not tests:
        print("No tests selected.")
        return 0

    print(
        f"Running {len(tests)} tests × {args.runs} runs against "
        f"{BACKEND_BASE}\n"
    )
    all_results = [run_test(t, args.runs) for t in tests]
    return print_summary(all_results)


if __name__ == "__main__":
    # Late import — only when actually running, so listing tests in
    # another tool doesn't hit the urllib namespace surprise.
    import urllib.error  # noqa: F401

    raise SystemExit(main())
