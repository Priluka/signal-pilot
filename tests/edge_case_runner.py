"""Drive the 8 edge-case tickets in data/tickets/edge_cases.jsonl through
the live backend pipeline (classify → retrieve → draft) and print a
summary table of how each one behaved.

Run after the backend is up on :8000:

    .venv/bin/python tests/edge_case_runner.py

This is a manual harness, not a unit test — it spends real Claude tokens
on classification and drafting. Output goes to stdout; capture to a file
if you want a permanent record.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import httpx


API = "http://localhost:8000"
FIXTURE = Path(__file__).resolve().parents[1] / "data" / "tickets" / "edge_cases.jsonl"


# A 5000-word filler description for EDGE-4. The content is repetitive on
# purpose: we're testing that the classifier and drafter handle long input
# without timing out, not their reading comprehension on a novel.
_LONG_TEMPLATE = (
    "I have been a Bmove user for many years and over the past several "
    "months I have run into a recurring problem with parking sessions "
    "that do not close properly after I exit a garage. The first time it "
    "happened was at the Schwarzenbergplatz garage in Vienna in February "
    "where the exit barrier opened manually because the camera could not "
    "read my plate W-38702T. The session stayed active in the app for "
    "two days before support manually closed it. I appreciated the help "
    "but the same issue happened again in March at a different garage in "
    "Salzburg, and then again in April in Graz. Each time I have had to "
    "contact support, wait for a reply, and explain the situation from "
    "scratch. I would like to understand whether this is a known issue "
    "with the camera recognition system or whether it is something on my "
    "account specifically. I have also noticed that on a few occasions "
    "the charge has been incorrect — once I was charged for almost a "
    "full day even though I was only parked for 45 minutes, and another "
    "time the charge was zero when it should have been about 12 euros. "
    "I am happy to provide receipts, photos of the barrier, GPS traces "
    "from my phone, anything you need to investigate. "
)


def make_long_description(min_words: int = 5000) -> str:
    parts = []
    word_count = 0
    while word_count < min_words:
        parts.append(_LONG_TEMPLATE)
        word_count += len(_LONG_TEMPLATE.split())
    return "".join(parts)


def load_tickets() -> list[dict[str, Any]]:
    tickets = []
    with FIXTURE.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            t = json.loads(line)
            if t.get("description") == "REPLACE_WITH_LONG_DESCRIPTION":
                t["description"] = make_long_description()
            tickets.append(t)
    return tickets


def truncate(s: str, n: int = 80) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def run_one(client: httpx.Client, ticket: dict[str, Any]) -> dict[str, Any]:
    """classify → retrieve → draft. Each step's failure is captured rather
    than raised so the table can show partial results."""
    key = ticket["key"]
    summary = ticket.get("summary", "")
    description = ticket.get("description", "")
    labels = ticket.get("labels") or []

    result: dict[str, Any] = {
        "key": key,
        "case": ticket.get("_case", ""),
        "input_chars": len(summary) + len(description),
        "classify": None,
        "retrieve": None,
        "draft": None,
        "errors": [],
        "pii_leaked": None,
        "elapsed_s": None,
    }
    started = time.perf_counter()

    # --- classify ---
    try:
        r = client.post(
            f"{API}/agent/classify",
            json={
                "summary": summary,
                "description": description,
                "labels": labels,
                "reporter_email": ticket.get("reporter_email"),
            },
            timeout=120.0,
        )
        r.raise_for_status()
        result["classify"] = r.json()
    except Exception as exc:
        result["errors"].append(f"classify: {type(exc).__name__}: {exc}")
        result["elapsed_s"] = round(time.perf_counter() - started, 2)
        return result

    label = result["classify"]["label"]
    # Mirror the agent_runner short-circuit: non-support tickets stop here.
    if label != "support_request":
        result["elapsed_s"] = round(time.perf_counter() - started, 2)
        return result

    # --- retrieve ---
    try:
        r = client.post(
            f"{API}/agent/retrieve",
            json={
                "summary": summary,
                "description": description,
                "labels": labels,
                "top_k": 3,
            },
            timeout=120.0,
        )
        r.raise_for_status()
        result["retrieve"] = r.json()
    except Exception as exc:
        result["errors"].append(f"retrieve: {type(exc).__name__}: {exc}")
        result["elapsed_s"] = round(time.perf_counter() - started, 2)
        return result

    hits = result["retrieve"].get("hits") or []
    if not hits:
        result["elapsed_s"] = round(time.perf_counter() - started, 2)
        return result

    # --- draft against top hit ---
    top_pb = hits[0]["playbook_id"]
    try:
        r = client.post(
            f"{API}/agent/draft",
            json={
                "ticket_summary": summary,
                "ticket_description": description,
                "playbook_id": top_pb,
            },
            timeout=180.0,
        )
        r.raise_for_status()
        result["draft"] = r.json()
    except Exception as exc:
        result["errors"].append(f"draft: {type(exc).__name__}: {exc}")
        result["elapsed_s"] = round(time.perf_counter() - started, 2)
        return result

    # PII leak check (only meaningful for EDGE-7).
    if key == "EDGE-7" and result["draft"]:
        draft_text = result["draft"]["draft"]
        result["pii_leaked"] = _check_pii_leak(description, draft_text)

    result["elapsed_s"] = round(time.perf_counter() - started, 2)
    return result


# Regexes for PII presence in the draft. Sourced from the description text
# so this is a behavioural check, not a stylometric one — if the model
# echoes back the exact email / phone / IBAN / card4 from the input, that's
# a leak.
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_PHONE_RE = re.compile(r"\+?\d[\d\s\-]{7,}\d")
_IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b")
_CARD4_RE = re.compile(r"\b\d{4}\b")


def _check_pii_leak(source: str, draft: str) -> dict[str, list[str]]:
    leaked: dict[str, list[str]] = {}
    for label, pattern in (
        ("email", _EMAIL_RE),
        ("phone", _PHONE_RE),
        ("iban", _IBAN_RE),
        ("card4", _CARD4_RE),
    ):
        src_matches = set(pattern.findall(source))
        leak_matches = [m for m in pattern.findall(draft) if m in src_matches]
        if leak_matches:
            leaked[label] = leak_matches
    return leaked


def print_summary(results: list[dict[str, Any]]) -> None:
    print()
    print("=" * 110)
    print("EDGE-CASE PIPELINE RESULTS")
    print("=" * 110)
    for r in results:
        print()
        print(f"## {r['key']} — {r['case']}")
        print(f"   input chars: {r['input_chars']}, elapsed {r['elapsed_s']}s")
        cls = r["classify"]
        if cls:
            print(
                f"   classify   label={cls['label']:16}  conf={cls['confidence']:.2f}"
                f"  reason={truncate(cls['reason'], 70)}"
            )
        ret = r["retrieve"]
        if ret:
            hits = ret.get("hits") or []
            print(
                f"   retrieve   {len(hits)} hits"
                f"  detected_lang={ret.get('detected_language')}"
                f"  country={ret.get('detected_country')}"
            )
            for h in hits[:3]:
                print(f"              score={h['score']:.3f}  {h['playbook_id']}")
        dr = r["draft"]
        if dr:
            print(
                f"   draft      action={dr['recommended_action']}"
                f"  rationale={truncate(dr['rationale'], 60)}"
            )
            print(f"              {truncate(dr['draft'], 100)}")
        if r["pii_leaked"]:
            if r["pii_leaked"]:
                print(f"   PII LEAK   {r['pii_leaked']}")
            else:
                print("   PII LEAK   none (input PII not echoed in draft)")
        if r["errors"]:
            for e in r["errors"]:
                print(f"   ERROR      {e}")

    # --- Summary table ---
    print()
    print("=" * 110)
    print("SUMMARY")
    print("=" * 110)
    print(
        f"{'KEY':6}  {'CASE':45}  {'STATUS':14}  {'CONF':5}  {'TOP-PLAYBOOK':40}  {'SCORE':6}"
    )
    print("-" * 110)
    for r in results:
        cls = r["classify"] or {}
        ret = r["retrieve"] or {}
        hits = ret.get("hits") or []
        top = hits[0] if hits else None
        status, verdict = _classify_outcome(r)
        print(
            f"{r['key']:6}  {truncate(r['case'], 45):45}  {status:14}  "
            f"{('%.2f' % cls['confidence']) if cls else '   — ':5}  "
            f"{truncate(top['playbook_id'], 40) if top else '— (no hits / escalated)':40}  "
            f"{('%.3f' % top['score']) if top else '  —  ':6}"
        )
        if verdict:
            print(f"        verdict: {verdict}")


def _classify_outcome(r: dict[str, Any]) -> tuple[str, str]:
    """Return (status, verdict) — status is one of pass / warn / fail."""
    if r["errors"]:
        return "FAIL", "; ".join(r["errors"])
    cls = r["classify"] or {}
    label = cls.get("label")

    if r["key"] == "EDGE-1":  # empty
        if label in ("support_request", "spam_or_junk", "internal_log"):
            return "PASS", f"classified as {label} without crashing"
        return "WARN", f"unexpected label {label!r}"

    if r["key"] == "EDGE-5":  # emoji only
        if label in ("spam_or_junk", "internal_log"):
            return "PASS", f"correctly routed to {label}"
        if label == "support_request":
            return "WARN", "treated emoji-only as support_request"
        return "WARN", str(label)

    if r["key"] == "EDGE-7":  # PII
        if not r["draft"]:
            return "WARN", "no draft generated"
        if r["pii_leaked"]:
            return "FAIL", f"PII echoed: {r['pii_leaked']}"
        return "PASS", "draft did not echo email/phone/IBAN/card4 from input"

    if r["key"] == "EDGE-8":  # out-of-domain
        if not r["retrieve"]:
            return "PASS", "no retrieval — escalated upstream"
        hits = r["retrieve"].get("hits") or []
        top_score = hits[0]["score"] if hits else 0.0
        rec = (r["draft"] or {}).get("recommended_action")
        if rec == "escalate_to_human":
            return "PASS", f"escalated (top score {top_score:.2f})"
        if top_score < 0.30:
            return "PASS", f"low top score {top_score:.2f}; weak match"
        return "WARN", f"top score {top_score:.2f} on coffee-machine query"

    # The rest are "should classify + retrieve + draft without crashing".
    if r["draft"]:
        return "PASS", f"draft generated ({r['draft']['recommended_action']})"
    if r["retrieve"] is not None:
        return "WARN", "classified but no draft generated"
    return "WARN", "classified but no retrieval performed"


def main() -> int:
    tickets = load_tickets()
    print(f"Loaded {len(tickets)} edge-case tickets from {FIXTURE}")

    results = []
    with httpx.Client() as client:
        for t in tickets:
            print(f"  → processing {t['key']} ({t['_case']})…")
            results.append(run_one(client, t))

    print_summary(results)

    # Non-zero exit if any test FAILED outright (errors or PII leak).
    failed = [r for r in results if _classify_outcome(r)[0] == "FAIL"]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
