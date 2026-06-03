"""FastAPI entry point for signal-pilot.

Run with:
    .venv/bin/uvicorn backend.main:app --reload --port 8000

Loads ``.env`` (for ``ANTHROPIC_API_KEY`` etc.), parses all playbooks at
startup, registers routers, and opens CORS for the local Vite dev server.
The embedding index is built lazily — only when an endpoint that needs
retrieval is hit — so the API is responsive immediately for knowledge
endpoints.
"""
from __future__ import annotations

import json
import logging
import sys
import uuid
from contextlib import asynccontextmanager
from contextvars import ContextVar
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing config so os.environ.get() picks up the values.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Make the repo root importable so ``core.*`` resolves under ``uvicorn``.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import config
from core.retrieval import discover_playbook_paths, load_playbook


# ---------------------------------------------------------------------------
# Structured logging — Phase 10.
# ---------------------------------------------------------------------------
#
# Every incoming HTTP request gets a short request_id (8-char uuid
# slice). The id flows via a ContextVar so background daemon threads
# spawned for SSE turn execution can pick it up too. A logging filter
# injects it into every log record's ``%(request_id)s`` placeholder
# so grep-by-id is possible across all the moving parts.

_request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


def current_request_id() -> str:
    return _request_id_var.get()


def set_request_id(value: str) -> None:
    _request_id_var.set(value)


class _RequestIdLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_var.get()
        return True


_LOG_FORMAT = (
    "%(asctime)s %(levelname)-5s [%(name)s] [rid=%(request_id)s] %(message)s"
)


def _configure_logging() -> None:
    from core.pii import PIIRedactionFilter

    root = logging.getLogger()
    # Tame uvicorn's own access log so our structured log is the
    # primary signal; uvicorn still logs to its own loggers.
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    handler.addFilter(_RequestIdLogFilter())
    # Phase 12.9 — PII redaction filter applied at root so every
    # module's logs are scrubbed before they hit any handler. Set
    # PII_REDACTION_DISABLED=1 in env when debugging.
    handler.addFilter(PIIRedactionFilter())
    # Replace any existing handlers configured by uvicorn so the format
    # is consistent across the process.
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    # Reduce noise from third parties.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


_configure_logging()


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Stamp each incoming request with a short id, surface it in the
    response (``X-Request-ID``) and in the ContextVar so log lines
    emitted by handlers / background threads picked up via
    ``set_request_id`` carry it. Honours an incoming ``X-Request-ID``
    header so callers (a reverse proxy, a frontend) can supply their
    own correlation id."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        rid = request.headers.get("x-request-id") or uuid.uuid4().hex[:8]
        token = _request_id_var.set(rid)
        try:
            response = await call_next(request)
        finally:
            _request_id_var.reset(token)
        response.headers["X-Request-ID"] = rid
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Phase 13.1 — reject requests whose declared Content-Length is
    larger than ``MAX_REQUEST_BYTES`` with 413 before the body is
    consumed. Cheap protection against a pasted 10MB blob exhausting
    the worker. Requests without a Content-Length header pass through
    (chunked streams are rare and not worth the complexity here)."""

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        cl = request.headers.get("content-length")
        if cl is not None:
            try:
                declared = int(cl)
            except ValueError:
                declared = 0
            if declared > config.MAX_REQUEST_BYTES:
                from fastapi.responses import JSONResponse

                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": (
                            f"Request body too large: {declared} bytes > "
                            f"limit {config.MAX_REQUEST_BYTES}"
                        )
                    },
                )
        return await call_next(request)

from .routers import (
    actions,
    agent,
    categories,
    chat,
    discovery,
    feedback,
    jira,
    playbooks,
    suggestions,
    tickets,
)


def _load_ticket_sample(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Bump anyio's default thread pool well above the 40-thread default.
    # Every sync FastAPI endpoint + every asyncio.to_thread call shares
    # this pool; 40 was too tight when the Agent Feed runs multiple
    # polling streams alongside the batch thread + SSE tails. With 200
    # the backend stays responsive even under aggressive concurrent use.
    from anyio import to_thread

    to_thread.current_default_thread_limiter().total_tokens = 200

    # Phase 11.3 — recover any chat turns left in 'streaming' from a
    # previous crashed process. Without this they'd appear forever
    # active in the UI.
    from core.chat_threads import recover_orphan_streaming_turns

    recovered = recover_orphan_streaming_turns()
    if recovered > 0:
        logging.getLogger(__name__).warning(
            "recovered %d orphan 'streaming' chat turns on startup",
            recovered,
        )

    paths = discover_playbook_paths(config.PLAYBOOKS_DIR)
    app.state.playbooks = [load_playbook(p) for p in paths]
    app.state.tickets = _load_ticket_sample(config.TICKET_SAMPLE_FILE)

    # Build the embedding index eagerly so the first burst of frontend
    # requests doesn't race to build it. Cached .npz on disk makes this
    # near-instant after the first run.
    from core.retrieval import build_index

    app.state.index = build_index()
    # Phase 17 — share the built index with the ``search_playbooks``
    # skill so it doesn't rebuild its own copy on first agent call.
    # Without this, the first chat turn that pivots to search_playbooks
    # after a playbook edit triggers a Voyage cold-start (3 min on
    # free-tier RPM) and the skill timeout (30 s) trips.
    from core.skills.external.search_playbooks import set_cached_index

    set_cached_index(app.state.index)
    yield

    # Phase 13.2 — graceful shutdown. Give in-flight turn daemons a
    # bounded window to finish naturally; any still running at the
    # deadline get persisted as error with a clear marker so the UI
    # doesn't show them as forever-streaming.
    from backend.routers.chat import (
        _running_turn_threads,
        _turn_threads_lock,
    )
    from core import chat_threads as _ct
    import time as _time

    grace = max(0, config.SHUTDOWN_GRACE_S)
    deadline = _time.time() + grace
    log = logging.getLogger(__name__)
    with _turn_threads_lock:
        alive = {
            tid: th
            for tid, th in _running_turn_threads.items()
            if th.is_alive()
        }
    if alive:
        log.warning(
            "shutdown drain: waiting up to %ds for %d in-flight turns",
            grace,
            len(alive),
        )
        for tid, th in alive.items():
            remaining = max(0, deadline - _time.time())
            if remaining <= 0:
                break
            th.join(timeout=remaining)
        # Anything still running missed the grace window.
        for tid, th in alive.items():
            if th.is_alive():
                log.warning(
                    "shutdown drain: turn %d did not finish, marking error",
                    tid,
                )
                try:
                    _ct.update_turn(
                        tid,
                        status="error",
                        error_message=(
                            "Backend shutdown while turn was in-flight"
                        ),
                    )
                except Exception:  # noqa: BLE001
                    pass
        log.info("shutdown drain complete")


app = FastAPI(
    title="Signal Pilot API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestSizeLimitMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    # Phase 11.4 — explicit allowlist from config. No wildcards.
    # Production deployments override CORS_ALLOWED_ORIGINS env var
    # with the real domain.
    allow_origins=config.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, object]:
    """Legacy liveness check — kept for backwards compat (tests, the
    smoke scripts, and any existing monitoring rules). Production
    callers should prefer ``/health/live`` (cheap) or ``/health/ready``
    (full dep check)."""
    return {
        "status": "ok",
        "playbooks_loaded": len(app.state.playbooks) if app.state.playbooks else 0,
        "tickets_loaded": len(app.state.tickets) if app.state.tickets else 0,
        "index_built": app.state.index is not None,
    }


@app.get("/metrics", tags=["meta"])
def prometheus_metrics() -> Response:
    """Prometheus scrape endpoint. Plain-text exposition format —
    Grafana / Datadog / Prometheus all consume this. Returns 200 even
    when no metrics have been observed yet (empty body is valid)."""
    from core.metrics import render_metrics

    body, content_type = render_metrics()
    return Response(content=body, media_type=content_type)


@app.get("/health/live", tags=["meta"])
def health_live() -> dict[str, object]:
    """Liveness probe — returns 200 if the process is up. No external
    dependencies. Use for container/k8s liveness checks where a 503
    should trigger a restart."""
    return {"status": "alive"}


@app.get("/health/ready", tags=["meta"])
def health_ready(response: Response) -> dict[str, object]:
    """Readiness probe — returns 200 only when every dependency the
    chat agent needs is healthy: DB read/write works, disk has
    headroom, and (optionally) Anthropic API is reachable. Returns
    503 with a per-component breakdown when anything is degraded so
    a monitoring system can alert on the specific failure."""
    from shutil import disk_usage

    checks: dict[str, dict[str, object]] = {}
    healthy = True

    # ---- DB write+read ----
    try:
        import sqlite3 as _sqlite3
        from core import chat_threads as _ct

        # Round-trip: create + read + delete a probe thread. Touches
        # SQLite via the same connection helper the real code uses, so
        # we exercise WAL + busy_timeout settings.
        probe = _ct.create_thread(title="(healthcheck-probe)")
        loaded = _ct.get_thread(probe.id)
        _ct.delete_thread(probe.id)
        if loaded is None or loaded.id != probe.id:
            raise RuntimeError("probe roundtrip mismatch")
        checks["db"] = {"ok": True}
    except Exception as exc:  # noqa: BLE001
        healthy = False
        checks["db"] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}

    # ---- Disk free space ----
    try:
        u = disk_usage(str(config.FEEDBACK_DB_PATH.parent))
        free_ratio = u.free / u.total if u.total > 0 else 0.0
        ok = free_ratio >= config.HEALTH_DISK_MIN_FREE_RATIO
        checks["disk"] = {
            "ok": ok,
            "free_bytes": u.free,
            "total_bytes": u.total,
            "free_ratio": round(free_ratio, 4),
            "min_required_ratio": config.HEALTH_DISK_MIN_FREE_RATIO,
        }
        if not ok:
            healthy = False
    except Exception as exc:  # noqa: BLE001
        healthy = False
        checks["disk"] = {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

    # ---- Anthropic reachability ----
    if config.HEALTH_PING_ANTHROPIC and config.ANTHROPIC_API_KEY:
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
            # ``models.list`` is the cheapest authenticated call. It
            # exercises auth + network + rate-limit posture without
            # spending tokens.
            client.models.list(limit=1)
            checks["anthropic"] = {"ok": True}
        except Exception as exc:  # noqa: BLE001
            healthy = False
            checks["anthropic"] = {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
    else:
        checks["anthropic"] = {"ok": True, "skipped": True}

    # ---- Index ----
    checks["playbook_index"] = {
        "ok": app.state.index is not None,
        "playbooks_loaded": (
            len(app.state.playbooks) if app.state.playbooks else 0
        ),
    }
    if app.state.index is None:
        healthy = False

    if not healthy:
        response.status_code = 503
    return {
        "status": "ready" if healthy else "degraded",
        "checks": checks,
    }


@app.post("/admin/playbooks/reload", tags=["meta"])
def reload_playbooks() -> dict[str, object]:
    """Re-read the playbook directory and rebuild the embedding index.

    Needed when frontmatter or body of a playbook changes at runtime —
    ``app.state.playbooks`` is populated once at startup and otherwise
    sticks until process restart. ``--reload`` only watches Python
    files, so editing a ``.md`` is invisible to a live backend without
    this hook.

    Builds new playbooks + index into locals first, then atomically
    swaps both onto ``app.state``. Concurrent /process callers see
    either the old pair or the new pair, never a torn mix.
    """
    from core.retrieval import build_index

    paths = discover_playbook_paths(config.PLAYBOOKS_DIR)
    new_playbooks = [load_playbook(p) for p in paths]
    new_index = build_index()
    app.state.playbooks = new_playbooks
    app.state.index = new_index
    # Phase 17 — keep search_playbooks cache in sync.
    from core.skills.external.search_playbooks import set_cached_index

    set_cached_index(new_index)
    with_skills = sum(
        1 for pb in new_playbooks if pb.metadata.get("allowed_skills")
    )
    return {
        "status": "ok",
        "playbooks_loaded": len(new_playbooks),
        "with_skills": with_skills,
    }


app.include_router(playbooks.router)
app.include_router(categories.router)
app.include_router(discovery.router)
app.include_router(tickets.router)
app.include_router(agent.router)
app.include_router(actions.router)
app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(suggestions.router)
app.include_router(jira.router)
