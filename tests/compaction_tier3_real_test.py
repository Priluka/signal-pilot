"""Tier 3 LLM-summarisation compaction — Phase 8E.

This is the only compaction tier that touches Anthropic. The earlier
Phase 6 tests covered Tier 1 (snip) and Tier 2 (drop oldest) with
synthetic histories and a patched threshold; Tier 3 was only validated
through the fallback path when the client was None.

Here we run ``_summarise_history`` directly with a real Anthropic
client and a chunk of synthetic prior-conversation messages that hold
concrete data points (plates, amounts, session ids). We assert:

  • The call returns a non-trivial summary (>200 chars).
  • At least 2 of the concrete data points appear in the summary
    verbatim — proof that the summariser preserves what we asked it to.
  • Latency is acceptable (<30s).

Cost: one Sonnet 4.6 call with ~5k input tokens, ~1.5k output cap.
Approx $0.05-0.10.

Run from project root:

    .venv/bin/python tests/compaction_tier3_real_test.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(_ROOT / ".env")

import config  # noqa: E402
from core.chat_agent import _summarise_history  # noqa: E402


# Concrete data points we expect the summariser to preserve. Picked
# to be distinctive enough that LLM paraphrase shouldn't drop them.
EXPECTED_DATA_POINTS = [
    "W-55123K",
    "ZG-1234-AB",
    "DT-20260527-882341",
    "usr-445521",
    "sess-88421",
    "€14.50",
]


def _build_synthetic_history() -> list[dict]:
    """A plausible 8-turn prior-conversation slice with concrete data
    points the agent looked up. The summariser must preserve these
    when collapsing them — that's the whole point of Tier 3."""
    msgs: list[dict] = []
    msgs.append({
        "role": "user",
        "content": "Provjeri Bmove za W-55123K — kupac se žali na duple naplate.",
    })
    msgs.append({
        "role": "assistant",
        "content": [
            {"type": "text", "text": "Tražim podatke."},
            {
                "type": "tool_use",
                "id": "call_1",
                "name": "bmove_user_lookup",
                "input": {"plate": "W-55123K"},
            },
        ],
    })
    msgs.append({
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "call_1",
            "content": (
                '{"user_id": "usr-445521", "email": "k***@gmail.com", '
                '"plate": "W-55123K", "active_session": true}'
            ),
        }],
    })
    msgs.append({
        "role": "assistant",
        "content": [{
            "type": "text",
            "text": (
                "Korisnik usr-445521 ima aktivnu sesiju. Idem provjeriti "
                "Datatrans transakcije."
            ),
        }],
    })
    msgs.append({
        "role": "assistant",
        "content": [{
            "type": "tool_use",
            "id": "call_2",
            "name": "datatrans_transaction",
            "input": {"reference": "DT-20260527-882341"},
        }],
    })
    msgs.append({
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "call_2",
            "content": (
                '{"transaction_id": "DT-20260527-882341", '
                '"amount": "€14.50", "status": "settled", '
                '"session_id": "sess-88421"}'
            ),
        }],
    })
    msgs.append({
        "role": "user",
        "content": "Provjeri i drugu plate ZG-1234-AB, isti kupac kaže.",
    })
    msgs.append({
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "call_3",
                "name": "bmove_user_lookup",
                "input": {"plate": "ZG-1234-AB"},
            },
        ],
    })
    msgs.append({
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": "call_3",
            "content": (
                '{"user_id": "usr-99812", "plate": "ZG-1234-AB", '
                '"found": true, "active_session": false}'
            ),
        }],
    })
    return msgs


def main() -> int:
    if not config.ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set")
        return 2
    from anthropic import Anthropic

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    msgs = _build_synthetic_history()
    print(f"synthetic history: {len(msgs)} messages")

    start = time.perf_counter()
    try:
        summary = _summarise_history(msgs, client=client)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: _summarise_history threw {type(exc).__name__}: {exc}")
        return 1
    elapsed = time.perf_counter() - start

    print(f"\nsummary returned in {elapsed:.1f}s, {len(summary)} chars:")
    print("-" * 60)
    print(summary)
    print("-" * 60)

    if elapsed > 30:
        print(f"FAIL: summarisation took {elapsed:.1f}s (>30s ceiling)")
        return 1
    if len(summary.strip()) < 200:
        print(f"FAIL: summary too short ({len(summary)} chars)")
        return 1

    preserved = []
    missing = []
    for dp in EXPECTED_DATA_POINTS:
        if dp.lower().replace("-", "") in summary.lower().replace("-", ""):
            preserved.append(dp)
        else:
            missing.append(dp)
    print(f"\npreserved data points: {preserved}")
    print(f"missing data points: {missing}")

    if len(preserved) < 2:
        print(
            f"FAIL: only {len(preserved)}/6 concrete data points preserved "
            "(need at least 2 — summary too aggressive)"
        )
        return 1

    print(f"\nPASS: tier 3 summary OK ({elapsed:.1f}s, {len(preserved)}/6 data points kept)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
