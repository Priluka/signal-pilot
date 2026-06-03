"""Central configuration for signal-pilot.

All tunables live here so swapping a model, a path, or a provider is a one-file change.
Environment variables override defaults — see README for a full list.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = ROOT_DIR / "data"
PLAYBOOKS_DIR: Path = DATA_DIR / "playbooks"
TICKETS_DIR: Path = DATA_DIR / "tickets"
CACHE_DIR: Path = DATA_DIR / "cache"
FEEDBACK_DB_PATH: Path = ROOT_DIR / "feedback.sqlite3"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Embeddings — swap provider by changing EMBEDDING_PROVIDER (local|voyage).
EMBEDDING_PROVIDER: str = os.environ.get("EMBEDDING_PROVIDER", "local")
EMBEDDING_MODEL_LOCAL: str = os.environ.get("EMBEDDING_MODEL_LOCAL", "BAAI/bge-m3")
EMBEDDING_MODEL_VOYAGE: str = os.environ.get("EMBEDDING_MODEL_VOYAGE", "voyage-3")
EMBEDDING_DEVICE: str = os.environ.get("EMBEDDING_DEVICE", "cpu")
EMBEDDING_CACHE_PATH: Path = CACHE_DIR / "playbook_embeddings.npz"

# Retrieval
TOP_K_RETRIEVAL: int = int(os.environ.get("TOP_K_RETRIEVAL", "3"))
MIN_RETRIEVAL_CONFIDENCE: float = float(os.environ.get("MIN_RETRIEVAL_CONFIDENCE", "0.25"))

# Claude API — three model slots so we can dial cost/latency/quality
# per surface without touching code. Defaults can be overridden in .env.
#   - Classifier stays on Haiku: ticket triage runs on every inbox row,
#     latency dominates UX, and the task is mostly pattern-matching.
#   - Drafter runs on Opus: the customer-facing draft must be the best
#     prose we can produce; quality dominates cost.
#   - Chat (Knowledge tab Q&A) also runs on Opus: this is the operator's
#     research surface, used many times per day to make real decisions
#     on real tickets, so quality dominates here too.
ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
CLASSIFIER_MODEL: str = os.environ.get("CLASSIFIER_MODEL", "claude-haiku-4-5-20251001")
# TEST MODE: drafter + chat on Sonnet 4.6 while iterating — Opus is
# the production target but burns through credit faster than we can
# justify during UI/flow testing. Flip back to ``claude-opus-4-7``
# when we want production-quality runs.
DRAFTER_MODEL: str = os.environ.get("DRAFTER_MODEL", "claude-sonnet-4-6")
CHAT_MODEL: str = os.environ.get("CHAT_MODEL", "claude-sonnet-4-6")
CLASSIFIER_MAX_TOKENS: int = 256
DRAFTER_MAX_TOKENS: int = 1500
CHAT_MAX_TOKENS: int = int(os.environ.get("CHAT_MAX_TOKENS", "2000"))
# Phase 9B — extended thinking budget for the chat agent. When > 0,
# the agent enables Sonnet's native "thinking" mode which lets Claude
# reason in a dedicated channel before producing the user-facing
# answer. Set to 0 to disable. Budget tokens count as output billing,
# so 2000 ≈ +$0.03 per turn upper bound.
CHAT_THINKING_BUDGET: int = int(
    os.environ.get("CHAT_THINKING_BUDGET", "2000")
)
# Phase 10 — hard cost cap per turn. If the cumulative Anthropic spend
# for a single turn (input + thinking + output tokens) crosses this
# ceiling, the agent loop aborts immediately and persists the partial
# answer with an error marker. Prevents a stuck/looping turn from
# burning the API budget. Set to 0 to disable the cap.
CHAT_TURN_COST_CAP_USD: float = float(
    os.environ.get("CHAT_TURN_COST_CAP_USD", "0.50")
)
# Per-IP rate limit on chat endpoints — count of new turns allowed
# inside ``CHAT_RATE_WINDOW_SECONDS`` from one client IP. Stops a
# misbehaving client (or accidental refresh loop) from flooding the
# backend.
CHAT_RATE_LIMIT_TURNS: int = int(
    os.environ.get("CHAT_RATE_LIMIT_TURNS", "20")
)
CHAT_RATE_WINDOW_SECONDS: int = int(
    os.environ.get("CHAT_RATE_WINDOW_SECONDS", "60")
)
# Anthropic retry policy. The SDK has internal retries but the
# defaults aren't aggressive enough on 429/529. We add an outer
# wrapper that catches RateLimit / Overloaded / APIConnection errors
# and retries with exponential backoff + jitter.
ANTHROPIC_MAX_RETRIES: int = int(os.environ.get("ANTHROPIC_MAX_RETRIES", "4"))
ANTHROPIC_INITIAL_BACKOFF_S: float = float(
    os.environ.get("ANTHROPIC_INITIAL_BACKOFF_S", "1.0")
)

# Phase 11.4 — CORS allowed origins. Comma-separated list of exact
# origins (no wildcards). Default keeps the Vite dev server for local
# development; production deployments set this to the operator-facing
# domain(s) explicitly.
CORS_ALLOWED_ORIGINS: list[str] = [
    o.strip()
    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if o.strip()
]

# Phase 11.5 — cumulative cost cap per chat thread. The agent rejects
# new turns on a thread whose summed cost crosses this ceiling, so a
# long-running thread can't silently bleed the budget. Operators see
# a clear 402 error and start a new thread.
CHAT_THREAD_COST_CAP_USD: float = float(
    os.environ.get("CHAT_THREAD_COST_CAP_USD", "5.00")
)

# Phase 11.2 — health-check thresholds. Disk usage below this fraction
# free is considered unhealthy (default: alert when >90% full).
HEALTH_DISK_MIN_FREE_RATIO: float = float(
    os.environ.get("HEALTH_DISK_MIN_FREE_RATIO", "0.10")
)
# Anthropic ping is a tiny ``models.list()`` call. Set to false to
# skip in environments where outbound HTTPS to api.anthropic.com isn't
# allowed at health-check time (e.g. air-gapped tests).
HEALTH_PING_ANTHROPIC: bool = (
    os.environ.get("HEALTH_PING_ANTHROPIC", "true").lower()
    in ("1", "true", "yes")
)

# Phase 12.9 — chat-thread retention. Threads older than this many
# days are eligible for the purge admin endpoint. Defaults to 90 days
# (a reasonable starting policy — adjust per regulation).
CHAT_THREAD_RETENTION_DAYS: int = int(
    os.environ.get("CHAT_THREAD_RETENTION_DAYS", "90")
)

# Phase 13.1 — request body size ceiling. A pasted 10MB blob can pin
# the JSON parser and starve the worker. 1 MiB is generous for any
# legitimate operator query.
MAX_REQUEST_BYTES: int = int(
    os.environ.get("MAX_REQUEST_BYTES", str(1024 * 1024))
)

# Phase 13.2 — graceful shutdown window. When SIGTERM arrives we stop
# accepting new turns and wait this many seconds for in-flight ones
# to finish naturally. Anything still running past the deadline is
# marked status='error' with a 'shutdown' marker.
SHUTDOWN_GRACE_S: int = int(os.environ.get("SHUTDOWN_GRACE_S", "20"))

# Phase 13.6 — spend watcher alert webhook. POST URL that receives a
# Slack-compatible JSON payload when the alert threshold trips. Set
# to empty to disable.
SPEND_WATCHER_WEBHOOK_URL: str = os.environ.get(
    "SPEND_WATCHER_WEBHOOK_URL", ""
)

# Planner — agent loop that drives tool_use. Defaults to the drafter model
# since it needs the same prose quality plus tool-selection reasoning.
PLANNER_MODEL: str = os.environ.get("PLANNER_MODEL", DRAFTER_MODEL)
PLANNER_MAX_TOKENS: int = int(os.environ.get("PLANNER_MAX_TOKENS", "2000"))
PLANNER_MAX_ITERATIONS: int = int(os.environ.get("PLANNER_MAX_ITERATIONS", "10"))
# Hard cap on successful write skills the planner will execute on one
# ticket. Defense in depth on top of MAX_ITERATIONS — a confused model
# can loop within the iteration budget; this stops grinding once the
# primary action (usually one customer-facing comment) is done.
PLANNER_MAX_WRITE_ACTIONS: int = int(
    os.environ.get("PLANNER_MAX_WRITE_ACTIONS", "2")
)

# Ticket sample for the Agent tab
TICKET_SAMPLE_FILE: Path = TICKETS_DIR / "sample.jsonl"
