"""Pre-demo smoke test — one script, 11 steps, exits non-zero on first
failure with a clear message naming the failing step.

Run before every demo:

    .venv/bin/python tests/smoke_test.py

Defaults to ``http://127.0.0.1:8000``; override with ``BASE_URL`` env var.

Each step is small and orthogonal: contract check (status code + shape +
one or two semantic assertions). The point isn't deep coverage — it's
"does the system look alive end-to-end" in ~30 seconds, including a
real Claude streaming call and a Jira REST probe.
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable

import httpx


BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
SAMPLE_PLAYBOOK_ID = "austrian-ticketless-open-session-at-exit__deee93"
SAMPLE_JIRA_KEY = os.environ.get("SMOKE_JIRA_KEY", "KAN-34")
CHAT_TIMEOUT_S = 90.0
DEFAULT_TIMEOUT_S = 30.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
class StepFailed(Exception):
    """Raised when a step's contract is violated. The message names the
    failing step and the specific assertion."""


def _get_json(path: str, timeout: float = DEFAULT_TIMEOUT_S) -> Any:
    with httpx.Client(timeout=timeout) as c:
        r = c.get(f"{BASE_URL}{path}")
        if r.status_code != 200:
            raise StepFailed(
                f"GET {path} → {r.status_code}: {r.text[:200]}"
            )
        try:
            return r.json()
        except json.JSONDecodeError as exc:
            raise StepFailed(f"GET {path} returned non-JSON: {exc}") from exc


def _post_json(path: str, body: dict, timeout: float = DEFAULT_TIMEOUT_S) -> Any:
    with httpx.Client(timeout=timeout) as c:
        r = c.post(f"{BASE_URL}{path}", json=body)
        if r.status_code != 200:
            raise StepFailed(
                f"POST {path} → {r.status_code}: {r.text[:200]}"
            )
        try:
            return r.json()
        except json.JSONDecodeError as exc:
            raise StepFailed(f"POST {path} returned non-JSON: {exc}") from exc


# ---------------------------------------------------------------------------
# Step functions
# ---------------------------------------------------------------------------
def step_health() -> str:
    data = _get_json("/health")
    if data.get("status") != "ok":
        raise StepFailed(f"/health status={data.get('status')!r}, expected 'ok'")
    if data.get("playbooks_loaded", 0) < 122:
        raise StepFailed(
            f"playbooks_loaded={data.get('playbooks_loaded')}, expected ≥122"
        )
    if not data.get("index_built"):
        raise StepFailed("index_built is falsy")
    return f"ok · playbooks={data['playbooks_loaded']} · index_built={data['index_built']}"


def step_playbooks_country_filter() -> str:
    data = _get_json("/playbooks?country=at")
    if not isinstance(data, list) or not data:
        raise StepFailed("expected non-empty list")
    # The filter is intentionally permissive — playbooks with
    # country_focus=['at'] OR ['other'] OR empty all pass. The full
    # corpus is 122; the filter must REJECT at least the ones that are
    # exclusively tagged for a different country (hr/it/de/sk only).
    if len(data) >= 122:
        raise StepFailed(
            f"country=at returned {len(data)} playbooks; expected < 122"
        )
    # Spot-check: at least one returned playbook must have 'at' in its
    # country_focus (otherwise the filter is matching only the 'other'
    # bucket — too loose).
    at_tagged = [p for p in data if "at" in (p.get("country_focus") or [])]
    if not at_tagged:
        raise StepFailed("no playbook in result actually has 'at' in country_focus")
    return f"ok · {len(data)} playbooks (at-tagged={len(at_tagged)})"


def step_playbook_detail() -> str:
    data = _get_json(f"/playbooks/{SAMPLE_PLAYBOOK_ID}")
    if data.get("id") != SAMPLE_PLAYBOOK_ID:
        raise StepFailed(f"id mismatch: got {data.get('id')!r}")
    if not data.get("title"):
        raise StepFailed("title missing")
    if not data.get("body") and not data.get("when_applies"):
        raise StepFailed("playbook body / when_applies both empty")
    return f"ok · {data['title'][:50]!r}"


def step_chat_answer() -> str:
    """Stream POST /chat/answer and verify the SSE protocol fires
    sources → delta(s) → done, that the model cites an Austrian
    playbook, and that the answer is agent-facing."""
    question = "How to handle stuck session in Vienna?"
    sources_received = False
    delta_count = 0
    done_received = False
    answer = ""
    cited_ids: list[str] = []
    started = time.monotonic()
    with httpx.stream(
        "POST",
        f"{BASE_URL}/chat/answer",
        json={"question": question, "top_k": 5},
        headers={"Accept": "text/event-stream"},
        timeout=CHAT_TIMEOUT_S,
    ) as resp:
        if resp.status_code != 200:
            raise StepFailed(
                f"POST /chat/answer → {resp.status_code}: "
                f"{resp.read().decode('utf-8', errors='replace')[:200]}"
            )
        buffer = ""
        for chunk in resp.iter_text():
            buffer += chunk
            while "\n\n" in buffer:
                raw, buffer = buffer.split("\n\n", 1)
                name = "message"
                data_lines: list[str] = []
                for line in raw.splitlines():
                    if line.startswith("event:"):
                        name = line[6:].strip()
                    elif line.startswith("data:"):
                        data_lines.append(line[5:].strip())
                if not data_lines:
                    continue
                try:
                    payload = json.loads("\n".join(data_lines))
                except json.JSONDecodeError:
                    continue
                if name == "sources":
                    sources_received = True
                elif name == "delta":
                    delta_count += 1
                    answer += payload.get("text", "")
                elif name == "done":
                    done_received = True
                    answer = payload.get("answer", answer)
                    cited_ids = payload.get("cited_ids", []) or []
                    break
                elif name == "error":
                    raise StepFailed(
                        f"chat stream error: {payload.get('message')!r}"
                    )
            if done_received:
                break
    elapsed = time.monotonic() - started
    if not sources_received:
        raise StepFailed("no sources event received")
    if delta_count == 0:
        raise StepFailed("no delta events received")
    if not done_received:
        raise StepFailed("no done event received")
    if not answer.strip():
        raise StepFailed("answer is empty")
    # The Vienna query should anchor on at least one Austrian playbook.
    at_cited = any(
        ("austrian" in cid.lower() or "vienna" in cid.lower() or "ticketless" in cid.lower())
        for cid in cited_ids
    )
    if not at_cited:
        raise StepFailed(
            f"no Austrian/Vienna playbook cited (got {cited_ids!r})"
        )
    # Agent-facing voice check: the answer should address the agent
    # (instructions to do something, not direct customer-talk).
    lower = answer.lower()
    agent_signals = [
        "ask the customer", "check", "verify", "escalate", "refund",
        "look up", "graylog", "zatraži", "provjeri", "eskaliraj",
    ]
    customer_voice_signals = [
        "contact support", "report the issue", "reach out to support",
        "kontaktiraj podršku", "kontaktirajte podršku",
    ]
    if any(t in lower for t in customer_voice_signals):
        raise StepFailed("answer addresses the customer, not the agent")
    if not any(t in lower for t in agent_signals):
        raise StepFailed("answer has no agent-facing instructions")
    return (
        f"ok · {len(answer)} chars · {delta_count} deltas · "
        f"cited={cited_ids[:3]} · {elapsed:.1f}s"
    )


def step_jira_process() -> str:
    data = _post_json(
        f"/jira/process/{SAMPLE_JIRA_KEY}",
        body={},
        timeout=CHAT_TIMEOUT_S,
    )
    if not data:
        raise StepFailed("empty response")
    if data.get("ticket_id") != SAMPLE_JIRA_KEY:
        raise StepFailed(
            f"ticket_id mismatch: got {data.get('ticket_id')!r}"
        )
    if not data.get("classification"):
        raise StepFailed("classification missing")
    # The classifier may auto-close (non-support); only require draft if
    # the ticket was classified as a support request.
    label = data["classification"].get("label")
    if label == "support_request":
        if not data.get("retrieval", {}).get("hits"):
            raise StepFailed("no retrieval hits despite support_request")
        if not data.get("draft"):
            raise StepFailed("no draft despite support_request")
        return (
            f"ok · {label} · draft={data['draft']['recommended_action']!r}"
        )
    return f"ok · classifier auto-closed as {label!r}"


def step_agent_sessions() -> str:
    data = _get_json("/agent/sessions")
    if not isinstance(data, list):
        raise StepFailed(f"expected list, got {type(data).__name__}")
    if not data:
        raise StepFailed("zero sessions — agent has processed nothing")
    # The session we just created in step_jira_process must be in here.
    keys = {s.get("ticket_id") for s in data}
    if SAMPLE_JIRA_KEY not in keys:
        raise StepFailed(
            f"{SAMPLE_JIRA_KEY} not in /agent/sessions ({len(data)} sessions)"
        )
    return f"ok · {len(data)} sessions · includes {SAMPLE_JIRA_KEY}"


def step_agent_activity() -> str:
    data = _get_json("/agent/activity?limit=200")
    if not isinstance(data, list):
        raise StepFailed(f"expected list, got {type(data).__name__}")
    if not data:
        raise StepFailed("zero activity events")
    event_types = {e.get("event_type") for e in data}
    if not (event_types & {"classified", "retrieved", "drafted"}):
        raise StepFailed(
            f"no agent events in feed; saw only {event_types!r}"
        )
    return f"ok · {len(data)} events · types={sorted(event_types)[:5]}"


def step_agent_config() -> str:
    data = _get_json("/agent/config")
    mode = data.get("mode")
    if mode not in {"shadow", "assisted", "autonomous"}:
        raise StepFailed(f"invalid mode={mode!r}")
    threshold = data.get("confidence_threshold")
    if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 1):
        raise StepFailed(f"invalid threshold={threshold!r}")
    return f"ok · mode={mode!r} · threshold={threshold}"


def step_playbook_modes() -> str:
    data = _get_json("/agent/playbook-modes")
    if not isinstance(data, list):
        raise StepFailed(f"expected list, got {type(data).__name__}")
    if len(data) < 122:
        raise StepFailed(f"got {len(data)} rows, expected ≥122")
    # Every row needs a playbook_id and a mode.
    bad = [r for r in data if not r.get("playbook_id") or not r.get("mode")]
    if bad:
        raise StepFailed(f"{len(bad)} rows missing playbook_id/mode")
    return f"ok · 122 rows"


def step_suggestions() -> str:
    data = _get_json("/suggestions")
    if not isinstance(data, list):
        raise StepFailed(f"expected list, got {type(data).__name__}")
    # Zero suggestions is valid for a fresh install — we just verify the
    # endpoint is reachable and well-formed. If non-empty, each entry
    # must have the canonical shape.
    if data:
        s0 = data[0]
        for k in ("id", "playbook_id", "type", "status"):
            if k not in s0:
                raise StepFailed(f"suggestion missing field {k!r}: {s0}")
    return f"ok · {len(data)} suggestions"


def step_jira_connection() -> str:
    data = _get_json("/jira/connection?probe=true", timeout=20.0)
    if not data.get("configured"):
        raise StepFailed("Jira credentials not configured in .env")
    if data.get("reachable") is not True:
        raise StepFailed(
            f"Jira not reachable: {data.get('detail') or 'no detail'}"
        )
    return f"ok · {data.get('url')} · project={data.get('project')!r}"


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
@dataclass
class Step:
    n: int
    name: str
    fn: Callable[[], str]


STEPS: list[Step] = [
    Step(1, "GET /health", step_health),
    Step(2, "GET /playbooks?country=at", step_playbooks_country_filter),
    Step(3, "GET /playbooks/<at-playbook>", step_playbook_detail),
    Step(4, "POST /chat/answer (Vienna stuck session)", step_chat_answer),
    Step(5, f"POST /jira/process/{SAMPLE_JIRA_KEY}", step_jira_process),
    Step(6, "GET /agent/sessions", step_agent_sessions),
    Step(7, "GET /agent/activity", step_agent_activity),
    Step(8, "GET /agent/config", step_agent_config),
    Step(9, "GET /agent/playbook-modes", step_playbook_modes),
    Step(10, "GET /suggestions", step_suggestions),
    Step(11, "GET /jira/connection?probe=true", step_jira_connection),
]


def main() -> int:
    print(f"Smoke test against {BASE_URL}")
    print(f"Sample playbook: {SAMPLE_PLAYBOOK_ID}")
    print(f"Sample Jira key: {SAMPLE_JIRA_KEY}")
    print("=" * 78)
    started = time.monotonic()
    for step in STEPS:
        label = f"[{step.n:>2}/11] {step.name}"
        print(f"{label:<58}", end=" ", flush=True)
        step_started = time.monotonic()
        try:
            result = step.fn()
        except StepFailed as exc:
            print("FAIL")
            print(f"        ✗ {exc}")
            print()
            print(f"PRE-DEMO SMOKE TEST FAILED at step {step.n}: {step.name}")
            return 1
        except httpx.RequestError as exc:
            print("FAIL")
            print(f"        ✗ network error: {exc}")
            print()
            print(
                f"PRE-DEMO SMOKE TEST FAILED at step {step.n}: "
                f"{step.name} (is the backend up at {BASE_URL}?)"
            )
            return 1
        except Exception as exc:  # noqa: BLE001
            print("FAIL")
            print(f"        ✗ unexpected: {type(exc).__name__}: {exc}")
            print()
            print(f"PRE-DEMO SMOKE TEST FAILED at step {step.n}: {step.name}")
            return 1
        dt = time.monotonic() - step_started
        print(f"PASS  ({dt:.1f}s)")
        print(f"        {result}")
    total = time.monotonic() - started
    print("=" * 78)
    print(f"All 11 steps PASS · total {total:.1f}s · ready for demo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
