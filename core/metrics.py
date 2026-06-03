"""Prometheus-style metrics for the chat agent — Phase 12.6.

Counters, histograms, and gauges that production monitoring (Grafana,
Datadog, anything scraping ``/metrics``) can chart and alert on. The
metrics are registered against the default ``prometheus_client``
registry, so the FastAPI endpoint just calls ``generate_latest()``.

Naming follows Prometheus conventions: lowercase, underscores, units
in the metric name (``_seconds``, ``_usd``, ``_total``). Buckets are
hand-picked for the typical signal-pilot turn:

  • Turn duration: 1s–120s, with finer buckets in the 1–30s sweet
    spot where most operator-facing turns land.
  • Skill duration: 0.05s–10s, since mocks return in <100ms and real
    HTTP skills land 0.5–5s.
  • Cost: 0.001–1.0 USD, log-ish spacing.

Module is import-safe even if ``prometheus_client`` isn't installed —
falls back to no-op shims so a missing dep can't break the chat path.
"""
from __future__ import annotations

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )
    _PROM_AVAILABLE = True
except ImportError:
    _PROM_AVAILABLE = False
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

    class _NoopMetric:
        def labels(self, *args, **kwargs):
            return self

        def inc(self, *args, **kwargs):
            pass

        def observe(self, *args, **kwargs):
            pass

    def Counter(*args, **kwargs):  # type: ignore[misc]
        return _NoopMetric()

    def Histogram(*args, **kwargs):  # type: ignore[misc]
        return _NoopMetric()

    def generate_latest() -> bytes:  # type: ignore[misc]
        return b""


# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------


CHAT_TURNS_TOTAL = Counter(
    "chat_turns_total",
    "Number of chat turns by terminal status.",
    ["status"],  # done | error | capped | interrupted
)

CHAT_TURN_DURATION = Histogram(
    "chat_turn_duration_seconds",
    "End-to-end duration of a chat turn (from request hit to status=done|error).",
    buckets=(1, 2, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 300),
)

CHAT_TURN_COST = Histogram(
    "chat_turn_cost_usd",
    "Anthropic cost per chat turn in USD.",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.10, 0.25, 0.50, 1.00, 2.00),
)

CHAT_SKILL_DURATION = Histogram(
    "chat_skill_duration_seconds",
    "Time a single skill invocation took inside the agent loop.",
    ["skill", "ok"],  # ok=true|false
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

CHAT_RATE_LIMIT_HITS = Counter(
    "chat_rate_limit_hits_total",
    "Number of HTTP 429 responses served by the chat rate limiter.",
)

CHAT_COST_CAP_HITS = Counter(
    "chat_cost_cap_hits_total",
    "Number of turns aborted because they crossed the cost cap.",
    ["scope"],  # turn | thread
)

CHAT_COMPACTION_HITS = Counter(
    "chat_compaction_hits_total",
    "Number of times the compaction layer fired, by tier.",
    ["tier"],  # 1 | 2 | 3
)

CHAT_ANTHROPIC_RETRIES = Counter(
    "chat_anthropic_retries_total",
    "Total Anthropic API retry attempts triggered by the backoff wrapper.",
    ["exception"],
)


def render_metrics() -> tuple[bytes, str]:
    """Return ``(body, content_type)`` for the /metrics endpoint."""
    return generate_latest(), CONTENT_TYPE_LATEST
