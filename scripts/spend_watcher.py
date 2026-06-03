"""Anthropic spend watcher — Phase 12.10.

Cron-friendly script that tallies the chat-side spend over the last
N hours by reading our own ``chat_turns.usage_json`` column. We don't
hit Anthropic's billing API (no public endpoint yet); instead we
trust the usage we already record per turn, which is exactly what we
charge through.

The script prints:

  • Total spend over the window
  • Top-spending threads (so the operator can spot one that's
    misbehaving)
  • The most expensive single turn
  • A breakdown by status (done / error / capped)

Exit code is non-zero when total spend crosses the warn / alert
thresholds, which lets the caller (a cron job, a CI healthcheck)
react with an email / Slack notification.

Usage:

    .venv/bin/python scripts/spend_watcher.py
    .venv/bin/python scripts/spend_watcher.py --hours 6 --warn 1.00 --alert 5.00
    .venv/bin/python scripts/spend_watcher.py --json   # machine-readable

Cron example (every 30 minutes):

    */30 * * * * cd /opt/signal-pilot && \\
        .venv/bin/python scripts/spend_watcher.py --warn 2 --alert 10 \\
        2>&1 | logger -t spend-watcher
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import config  # noqa: E402


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(config.FEEDBACK_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def collect(hours: int) -> dict:
    """Walk chat_turns rows in the window and tally costs. Returns a
    dict ready for print or JSON output."""
    cutoff_dt = datetime.now(timezone.utc) - timedelta(hours=hours)
    cutoff = cutoff_dt.isoformat(timespec="seconds")
    conn = _connect()
    rows = conn.execute(
        "SELECT id, thread_id, status, usage_json, created_at "
        "FROM chat_turns "
        "WHERE created_at >= ?",
        (cutoff,),
    ).fetchall()
    conn.close()

    total = 0.0
    by_status: dict[str, dict[str, float]] = {}
    by_thread: dict[int, float] = {}
    most_expensive: tuple[int, float] = (0, 0.0)

    for row in rows:
        try:
            usage = json.loads(row["usage_json"] or "{}")
        except Exception:  # noqa: BLE001
            usage = {}
        cost = float(usage.get("cost_usd") or 0.0)
        total += cost
        st = row["status"]
        bucket = by_status.setdefault(st, {"count": 0, "cost": 0.0})
        bucket["count"] += 1
        bucket["cost"] += cost
        by_thread[row["thread_id"]] = by_thread.get(row["thread_id"], 0) + cost
        if cost > most_expensive[1]:
            most_expensive = (row["id"], cost)

    top_threads = sorted(by_thread.items(), key=lambda kv: -kv[1])[:10]
    return {
        "window_hours": hours,
        "cutoff_utc": cutoff,
        "total_usd": round(total, 6),
        "turn_count": len(rows),
        "by_status": {
            st: {"count": b["count"], "cost_usd": round(b["cost"], 6)}
            for st, b in by_status.items()
        },
        "top_threads": [
            {"thread_id": tid, "cost_usd": round(c, 6)}
            for tid, c in top_threads
        ],
        "most_expensive_turn": {
            "turn_id": most_expensive[0],
            "cost_usd": round(most_expensive[1], 6),
        },
    }


def render_human(report: dict, warn: float, alert: float) -> None:
    print(
        f"Spend window: last {report['window_hours']}h (since "
        f"{report['cutoff_utc']})"
    )
    print(f"Total: ${report['total_usd']} across {report['turn_count']} turns")
    if report["total_usd"] >= alert:
        print(f"  ALERT: total >= alert threshold ${alert}")
    elif report["total_usd"] >= warn:
        print(f"  WARN:  total >= warn threshold ${warn}")
    print("\nBy status:")
    for st, b in report["by_status"].items():
        print(f"  {st:12} {b['count']:4} turns  ${b['cost_usd']:.4f}")
    print("\nTop threads by spend:")
    for t in report["top_threads"]:
        print(f"  thread #{t['thread_id']:<6}  ${t['cost_usd']:.4f}")
    me = report["most_expensive_turn"]
    print(f"\nMost expensive single turn: #{me['turn_id']} = ${me['cost_usd']}")


def _post_webhook(url: str, payload: dict) -> None:
    """Fire a Slack-compatible webhook with the report. The Slack
    incoming-webhook contract accepts a JSON body with a ``text`` field
    (rendered as the message). We include the full structured report
    in an ``attachments`` block too so richer integrations have
    everything they need."""
    import urllib.request

    text = (
        f":money_with_wings: signal-pilot spend alert — "
        f"${payload['total_usd']:.4f} in last "
        f"{payload['window_hours']}h "
        f"({payload['turn_count']} turns)"
    )
    body = {
        "text": text,
        "attachments": [
            {
                "color": "danger",
                "title": "Spend report",
                "text": "```" + json.dumps(payload, indent=2) + "```",
                "mrkdwn_in": ["text"],
            }
        ],
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        resp.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--warn", type=float, default=2.0)
    parser.add_argument("--alert", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--webhook",
        default=config.SPEND_WATCHER_WEBHOOK_URL or None,
        help=(
            "POST URL receiving a Slack-compatible JSON alert when "
            "total spend crosses the alert threshold. Defaults to "
            "SPEND_WATCHER_WEBHOOK_URL env var."
        ),
    )
    args = parser.parse_args()

    report = collect(args.hours)
    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        render_human(report, warn=args.warn, alert=args.alert)

    # Phase 13.6 — fire the webhook only on alert-level breach.
    # Warn-level stays silent in the chat channel; a cron tail
    # collects those for later review.
    if args.webhook and report["total_usd"] >= args.alert:
        try:
            _post_webhook(args.webhook, report)
            print(f"\nalert webhook delivered to {args.webhook}")
        except Exception as exc:  # noqa: BLE001
            # Don't fail the cron job just because the webhook is
            # down — exit code still communicates severity.
            print(f"\nwebhook delivery failed: {exc}", file=sys.stderr)

    # Exit code communicates threshold breach to the cron job.
    if report["total_usd"] >= args.alert:
        return 2
    if report["total_usd"] >= args.warn:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
