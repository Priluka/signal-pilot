"""End-to-end test of the three agent modes against the LIVE Jira instance.

Creates four fresh tickets in the configured Jira project, switches the
agent through shadow → assisted → autonomous (above & below threshold),
runs the pipeline against each ticket, and verifies that the comment the
agent posts (or doesn't post) matches the mode.

Side effects:
  * Creates 4 Jira issues in the configured project (KAN by default).
    They are NOT auto-deleted — the comments are useful evidence; delete
    them manually if you want a clean board.
  * Spends Claude tokens (4× classify + 3× retrieve + 3× draft).
  * Persists the mode changes in agent_config; the script resets to
    'shadow' at the end so the next run starts from a known state.

Run with the backend up on :8000:

    .venv/bin/python tests/jira_mode_e2e.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

API = "http://localhost:8000"

JIRA_URL = os.environ["JIRA_URL"].rstrip("/")
JIRA_EMAIL = os.environ["JIRA_EMAIL"]
JIRA_TOKEN = os.environ["JIRA_TOKEN"]
JIRA_PROJECT = os.environ["JIRA_PROJECT"]


# A summary + description that we KNOW the corpus matches with high
# confidence — the Austrian stuck-session pattern consistently classifies
# as support_request ~0.95 and retrieves into the AT playbooks.
TEST_SUMMARY = "Parking session still open after exit (mode E2E test)"
TEST_DESCRIPTION = (
    "Hello, I left the Schwarzenbergplatz garage in Vienna last night at 21:30 "
    "but the Bmove app still shows my session as active. The exit barrier "
    "opened manually because the licence plate camera did not pick up my "
    "plate W-99012X. Please close the session and adjust the charge. Thank you."
)


def _adf(text: str) -> dict:
    """Wrap plain text in the minimum ADF envelope Jira's REST v3 accepts."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ],
    }


def jira_create_issue(client: httpx.Client, summary: str, description: str) -> str:
    """Create one Jira issue. Returns the new issue key."""
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT},
            "summary": summary,
            "description": _adf(description),
            "issuetype": {"name": "Task"},
        }
    }
    r = client.post("/rest/api/3/issue", json=payload, timeout=30.0)
    if r.status_code >= 300:
        raise RuntimeError(f"Jira create issue failed: {r.status_code} {r.text}")
    return r.json()["key"]


def jira_get_comments(client: httpx.Client, key: str) -> list[dict[str, Any]]:
    r = client.get(f"/rest/api/3/issue/{key}/comment", timeout=30.0)
    r.raise_for_status()
    return r.json().get("comments") or []


def _adf_to_text(node: Any) -> str:
    """Flatten an ADF comment body to plain text for content inspection."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(_adf_to_text(n) for n in node)
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text") or ""
    return _adf_to_text(node.get("content"))


def set_agent_config(
    client: httpx.Client, mode: str, threshold: float | None = None
) -> None:
    payload: dict[str, Any] = {"mode": mode}
    if threshold is not None:
        payload["confidence_threshold"] = threshold
    r = client.put(f"{API}/agent/config", json=payload, timeout=30.0)
    r.raise_for_status()


def process_ticket(client: httpx.Client, key: str) -> dict[str, Any]:
    r = client.post(f"{API}/jira/process/{key}", timeout=180.0)
    r.raise_for_status()
    return r.json()


# ---------------------------------------------------------------------------
# Test steps
# ---------------------------------------------------------------------------

def run_step(
    *,
    label: str,
    expected: str,
    mode: str,
    threshold: float | None,
    expect_comment: bool,
    expect_draft_prefix: bool | None,
) -> dict[str, Any]:
    """One step of the matrix. Creates a ticket, sets mode + threshold,
    processes it, reads back the comments, and judges pass/fail.

    ``expect_comment``        — True if there must be ≥1 comment after process
    ``expect_draft_prefix``   — True/False to require/forbid a '[DRAFT'
                                 prefix; None means 'don't care' (used when
                                 ``expect_comment`` is False)
    """
    print(f"\n→ {label}")
    print(f"  mode={mode}  threshold={threshold}  expected={expected}")

    jira_client = httpx.Client(
        base_url=JIRA_URL,
        auth=(JIRA_EMAIL, JIRA_TOKEN),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    backend = httpx.Client()

    try:
        # 1. Configure mode + threshold
        set_agent_config(backend, mode, threshold)

        # 2. Create a fresh Jira ticket
        key = jira_create_issue(jira_client, f"{TEST_SUMMARY} [{label}]", TEST_DESCRIPTION)
        print(f"  created  {key}")
        # Tiny pause — Jira indexing isn't instantaneous and the REST GET
        # right after a POST occasionally 404s otherwise.
        time.sleep(1.0)

        # 3. Run the agent pipeline through the backend
        session = process_ticket(backend, key)
        classification = session.get("classification") or {}
        confidence = float(classification.get("confidence") or 0.0)
        print(f"  classify confidence={confidence:.2f}  label={classification.get('label')}")

        # Auto-post happens inside the backend; small grace period in case
        # the comment-write happens after the response (it doesn't today,
        # but better safe than racing).
        time.sleep(0.5)

        # 4. Read comments off Jira
        comments = jira_get_comments(jira_client, key)
        comment_texts = [_adf_to_text(c.get("body")).strip() for c in comments]
        print(f"  comments {len(comments)} found")
        for t in comment_texts:
            print(f"           {t[:110]!r}")

        # 5. Verdict
        passed = True
        notes = []
        if expect_comment:
            if not comment_texts:
                passed = False
                notes.append("no comment was posted")
            else:
                has_draft_prefix = any(t.startswith("[DRAFT") for t in comment_texts)
                if expect_draft_prefix is True and not has_draft_prefix:
                    passed = False
                    notes.append("comment missing [DRAFT prefix")
                elif expect_draft_prefix is False and has_draft_prefix:
                    passed = False
                    notes.append("comment unexpectedly has [DRAFT prefix")
        else:
            if comment_texts:
                passed = False
                notes.append(f"unexpected comment(s) posted: {comment_texts[0][:60]!r}…")

        actual = (
            "no comment"
            if not comments
            else f"{len(comments)} comment(s)"
            + (" with [DRAFT prefix" if any(t.startswith("[DRAFT") for t in comment_texts) else " without [DRAFT prefix")
        )

        return {
            "label": label,
            "key": key,
            "mode": mode,
            "threshold": threshold,
            "confidence": confidence,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "notes": "; ".join(notes),
        }
    finally:
        jira_client.close()
        backend.close()


def main() -> int:
    print(f"Target Jira: {JIRA_URL} project {JIRA_PROJECT}")
    print(f"Backend:     {API}")

    results = []
    results.append(
        run_step(
            label="shadow",
            expected="no Jira comment (draft only in inbox)",
            mode="shadow",
            threshold=None,
            expect_comment=False,
            expect_draft_prefix=None,
        )
    )
    results.append(
        run_step(
            label="assisted",
            expected="no Jira comment until operator approves",
            mode="assisted",
            threshold=None,
            expect_comment=False,
            expect_draft_prefix=None,
        )
    )
    results.append(
        run_step(
            label="autonomous-above-threshold",
            expected="clean comment (no [DRAFT] prefix, conf ≥ 0.50)",
            mode="autonomous",
            threshold=0.50,
            expect_comment=True,
            expect_draft_prefix=False,
        )
    )
    results.append(
        run_step(
            label="autonomous-below-threshold",
            expected="no Jira comment (falls back to assisted, operator decides)",
            mode="autonomous",
            threshold=0.99,
            expect_comment=False,
            expect_draft_prefix=None,
        )
    )

    # Always reset to shadow afterwards so the agent doesn't keep
    # auto-posting comments to whatever the next operator processes.
    print("\nResetting to shadow + threshold=0.60")
    with httpx.Client() as backend:
        set_agent_config(backend, "shadow", 0.60)

    # --- Summary table ---
    print()
    print("=" * 130)
    print("MODE E2E RESULTS")
    print("=" * 130)
    print(
        f"{'TEST':30}  {'KEY':8}  {'CONF':5}  {'EXPECTED':50}  {'ACTUAL':30}  {'RESULT'}"
    )
    print("-" * 130)
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        print(
            f"{r['label']:30}  {r['key']:8}  "
            f"{('%.2f' % r['confidence']):5}  "
            f"{r['expected'][:50]:50}  "
            f"{r['actual'][:30]:30}  "
            f"{status}"
        )
        if r["notes"]:
            print(f"  ↳ {r['notes']}")

    failed = sum(1 for r in results if not r["passed"])
    print()
    print(f"{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
