"""SQLite-backed store for the Agent tab's per-ticket workflow state.

One row per ticket. Each row holds the most recent classification result,
the retrieval result + chosen playbook, the generated draft, the
operator's edited text, and the final feedback status (approved / edited /
rejected). Endpoints in ``backend/routers/agent.py`` and
``backend/routers/feedback.py`` upsert into this table on every step so
navigating away and coming back restores the workflow exactly where the
operator left it.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import config


_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_sessions (
    ticket_id           TEXT PRIMARY KEY,
    classification_json TEXT,
    retrieval_json      TEXT,
    draft_json          TEXT,
    draft_playbook_id   TEXT,
    edited_text         TEXT,
    feedback_status     TEXT,
    updated_at          TEXT NOT NULL,
    started_at          TEXT,
    classified_at       TEXT,
    retrieved_at        TEXT,
    drafted_at          TEXT,
    feedback_at         TEXT,
    auto_posted_at      TEXT,
    processed_mode      TEXT,
    planner_status      TEXT,
    planner_error       TEXT,
    planner_updated_at  TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_updated ON agent_sessions(updated_at);
"""


# Columns added after v0.1. The migration loop adds them as TEXT if missing.
_LATER_COLUMNS: tuple[str, ...] = (
    "processed_mode",
    "planner_status",
    "planner_error",
    "planner_updated_at",
    # Which writer path the session is on, decided at retrieve time:
    #   'drafter' → classic single-LLM draft, no skills layer
    #   'planner' → tool_use loop produces the final reply via skills
    # Mutually exclusive — never both. NULL only for pre-routing sessions
    # (legacy rows written before this column existed).
    "routing",
    # First failed step + its exception message. Without these, a
    # classify/retrieve/draft crash leaves the session row stuck in a
    # half-populated state — frontend reads it on refresh, sees
    # ``classified_at`` null, and renders 'Classifying…' spinner
    # forever. Planner failures get persisted separately via
    # ``planner_status='failed'`` + ``planner_error``; these two cover
    # the earlier steps too.
    "error_step",
    "error_message",
)


_TIMESTAMP_COLUMNS = (
    "started_at",
    "classified_at",
    "retrieved_at",
    "drafted_at",
    "feedback_at",
    # Set when autonomous mode posts the final (non-draft) Jira comment.
    # Different from ``feedback_at`` so we can tell 'agent decided' apart
    # from 'human decided' for the same approved-status session.
    "auto_posted_at",
)


@dataclass
class AgentSessionRecord:
    ticket_id: str
    classification: dict[str, Any] | None
    retrieval: dict[str, Any] | None
    draft: dict[str, Any] | None
    draft_playbook_id: str | None
    edited_text: str | None
    feedback_status: str | None
    updated_at: str
    started_at: str | None = None
    classified_at: str | None = None
    retrieved_at: str | None = None
    drafted_at: str | None = None
    feedback_at: str | None = None
    auto_posted_at: str | None = None
    # Effective agent mode (shadow / assisted / autonomous) at the time
    # this ticket was processed. Stored so the inbox can show what each
    # ticket was handled under — relevant when the operator switches modes
    # frequently or sets per-playbook overrides.
    processed_mode: str | None = None
    # Planner outcome — written by core.agent_runner after planner.run().
    # status ∈ {done, awaiting_approval, failed, max_iterations}; error
    # carries the exception detail when status='failed'. UI surfaces a
    # banner whenever status is not 'done' so a silent loop failure
    # can't hide.
    planner_status: str | None = None
    planner_error: str | None = None
    planner_updated_at: str | None = None
    # Writer path chosen at retrieve time: 'drafter' for classic single-LLM
    # reply, 'planner' for tool_use loop with skills. Mutually exclusive —
    # the runner picks one and never both. NULL on legacy rows from before
    # this column existed.
    routing: str | None = None
    # First failed step ('classify' | 'retrieve' | 'draft' | 'planner')
    # and the exception message. Persisted by the runner whenever a step
    # crashes, so a page refresh after a credit-limit error still shows
    # the failure inline instead of an infinite spinner.
    error_step: str | None = None
    error_message: str | None = None


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate_if_needed(conn: sqlite3.Connection) -> None:
    rows = conn.execute("PRAGMA table_info(agent_sessions)").fetchall()
    cols = {row[1] for row in rows}
    for col in _TIMESTAMP_COLUMNS + _LATER_COLUMNS:
        if col not in cols:
            conn.execute(f"ALTER TABLE agent_sessions ADD COLUMN {col} TEXT")


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)
        _migrate_if_needed(conn)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row_get(row: sqlite3.Row, key: str) -> Any:
    return row[key] if key in row.keys() else None


def _row_to_record(row: sqlite3.Row) -> AgentSessionRecord:
    return AgentSessionRecord(
        ticket_id=row["ticket_id"],
        classification=json.loads(row["classification_json"]) if row["classification_json"] else None,
        retrieval=json.loads(row["retrieval_json"]) if row["retrieval_json"] else None,
        draft=json.loads(row["draft_json"]) if row["draft_json"] else None,
        draft_playbook_id=row["draft_playbook_id"],
        edited_text=row["edited_text"],
        feedback_status=row["feedback_status"],
        updated_at=row["updated_at"],
        started_at=_row_get(row, "started_at"),
        classified_at=_row_get(row, "classified_at"),
        retrieved_at=_row_get(row, "retrieved_at"),
        drafted_at=_row_get(row, "drafted_at"),
        feedback_at=_row_get(row, "feedback_at"),
        auto_posted_at=_row_get(row, "auto_posted_at"),
        processed_mode=_row_get(row, "processed_mode"),
        planner_status=_row_get(row, "planner_status"),
        planner_error=_row_get(row, "planner_error"),
        planner_updated_at=_row_get(row, "planner_updated_at"),
        routing=_row_get(row, "routing"),
        error_step=_row_get(row, "error_step"),
        error_message=_row_get(row, "error_message"),
    )


def _ensure_row(conn: sqlite3.Connection, ticket_id: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO agent_sessions (ticket_id, updated_at) VALUES (?, ?)",
        (ticket_id, _now()),
    )


def list_sessions(
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> list[AgentSessionRecord]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM agent_sessions ORDER BY updated_at DESC"
        ).fetchall()
    return [_row_to_record(r) for r in rows]


def get_session(
    ticket_id: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> AgentSessionRecord | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM agent_sessions WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
    return _row_to_record(row) if row else None


def mark_started(
    ticket_id: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> AgentSessionRecord:
    """Stamp ``started_at`` at the beginning of batch processing so per-step
    durations can be displayed in the timeline."""
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        conn.execute(
            "UPDATE agent_sessions SET started_at = ?, updated_at = ? WHERE ticket_id = ?",
            (now, now, ticket_id),
        )
        row = conn.execute(
            "SELECT * FROM agent_sessions WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
    return _row_to_record(row)


def upsert_classification(
    ticket_id: str,
    classification: dict[str, Any],
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> AgentSessionRecord:
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        # New classification invalidates everything downstream (retrieval was
        # tied to a previous classification, draft was tied to that retrieval).
        # A successful classify also invalidates any persisted error from a
        # prior attempt — fresh run starts clean.
        conn.execute(
            "UPDATE agent_sessions SET classification_json = ?, classified_at = ?, "
            "retrieval_json = NULL, retrieved_at = NULL, "
            "draft_json = NULL, draft_playbook_id = NULL, drafted_at = NULL, "
            "edited_text = NULL, feedback_status = NULL, feedback_at = NULL, "
            "error_step = NULL, error_message = NULL, "
            "updated_at = ? WHERE ticket_id = ?",
            (json.dumps(classification), now, now, ticket_id),
        )
        row = conn.execute(
            "SELECT * FROM agent_sessions WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
    return _row_to_record(row)


def upsert_retrieval(
    ticket_id: str,
    retrieval: dict[str, Any],
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> AgentSessionRecord:
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        # New retrieval invalidates the existing draft / edits / feedback —
        # those were tied to a specific playbook list that may now differ.
        conn.execute(
            "UPDATE agent_sessions SET retrieval_json = ?, retrieved_at = ?, "
            "draft_json = NULL, draft_playbook_id = NULL, drafted_at = NULL, "
            "edited_text = NULL, feedback_status = NULL, feedback_at = NULL, "
            "routing = NULL, "
            "updated_at = ? WHERE ticket_id = ?",
            (json.dumps(retrieval), now, now, ticket_id),
        )
        row = conn.execute(
            "SELECT * FROM agent_sessions WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
    return _row_to_record(row)


def upsert_draft(
    ticket_id: str,
    playbook_id: str,
    draft: dict[str, Any],
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> AgentSessionRecord:
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        # New draft resets edits/feedback that referenced the previous one.
        conn.execute(
            "UPDATE agent_sessions SET draft_json = ?, draft_playbook_id = ?, drafted_at = ?, "
            "edited_text = NULL, feedback_status = NULL, feedback_at = NULL, "
            "updated_at = ? WHERE ticket_id = ?",
            (json.dumps(draft), playbook_id, now, now, ticket_id),
        )
        row = conn.execute(
            "SELECT * FROM agent_sessions WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
    return _row_to_record(row)


def upsert_feedback(
    ticket_id: str,
    status: str,
    edited_text: str | None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> AgentSessionRecord | None:
    """Recorded when the operator clicks Approve / Save edit / Reject.
    Returns None if no agent_session row exists for the ticket (which would
    mean the feedback came in without a draft — unusual but allowed)."""
    if status not in ("approved", "edited", "rejected"):
        raise ValueError(f"invalid feedback status: {status!r}")
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        conn.execute(
            "UPDATE agent_sessions SET feedback_status = ?, edited_text = ?, "
            "feedback_at = ?, updated_at = ? WHERE ticket_id = ?",
            (status, edited_text, now, now, ticket_id),
        )
        row = conn.execute(
            "SELECT * FROM agent_sessions WHERE ticket_id = ?", (ticket_id,)
        ).fetchone()
    return _row_to_record(row) if row else None


def delete_session(
    ticket_id: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> bool:
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM agent_sessions WHERE ticket_id = ?", (ticket_id,))
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Derived status — single source of truth used by the Agent Feed inbox
# ---------------------------------------------------------------------------
# 7 possible states as visible to the operator:
#   pending       — no session yet (batch hasn't reached this ticket)
#   in_progress   — partial: classified but no draft yet, still being processed
#   skipped       — classifier said internal_log or spam (no reply needed)
#   auto_resolved — draft recommended_action == 'auto_close'
#   auto_drafted  — draft recommended_action == 'send_draft' (ready to send)
#   needs_review  — draft recommended_action == 'send_with_review'
#   escalated     — draft recommended_action == 'escalate_to_human'
#   approved      — operator clicked Approve (with or without edits)
#   rejected      — operator clicked Reject
def derive_status(record: AgentSessionRecord | None) -> str:
    if record is None:
        return "pending"
    if record.feedback_status == "approved" or record.feedback_status == "edited":
        return "approved"
    if record.feedback_status == "rejected":
        return "rejected"
    classification = record.classification or {}
    label = classification.get("label")
    if label in ("internal_log", "spam_or_junk"):
        return "skipped"
    # Planner path: drafter never runs, so record.draft is NULL. Derive
    # the terminal state from planner_status — otherwise a shadow-
    # completed or autonomous-resolved session falls through to
    # 'in_progress' and the inbox keeps it bold forever.
    if record.routing == "planner":
        if record.planner_status == "done":
            # 'auto_resolved' implies the agent ran autonomously. In
            # assisted mode the planner only reaches 'done' AFTER the
            # operator approved each queued write — calling that
            # 'auto-sent' would lie about who decided. Shadow stays in
            # the autonomous bucket because nothing was actually sent;
            # it's a dry-run completion, not an operator decision.
            if record.processed_mode == "assisted":
                return "approved"
            return "auto_resolved"
        if record.planner_status == "awaiting_approval":
            return "needs_review"
        if record.planner_status in ("failed", "max_iterations"):
            # No 'failed' pill in the operator UI; route through
            # needs_review so the unread badge surfaces the regression
            # instead of swallowing it as 'in_progress'.
            return "needs_review"
        if record.classification:
            return "in_progress"
        return "pending"
    # Drafter path (or pre-routing legacy rows with a draft).
    if record.draft:
        action = record.draft.get("recommended_action")
        if action == "auto_close":
            return "auto_resolved"
        if action == "escalate_to_human":
            return "escalated"
        if action == "send_draft":
            return "auto_drafted"
        if action == "send_with_review":
            return "needs_review"
        # Unknown action falls through to needs_review for safety.
        return "needs_review"
    if record.classification:
        return "in_progress"
    return "pending"


def mark_processed_mode(
    ticket_id: str,
    mode: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> None:
    """Record which mode the agent was in when this ticket got processed.
    Called from ``agent_runner.process_ticket`` once per ticket — used by
    the inbox UI to badge each ticket with its handling mode."""
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE agent_sessions SET processed_mode = ?, updated_at = ? "
            "WHERE ticket_id = ?",
            (mode, now, ticket_id),
        )


def mark_top_playbook(
    ticket_id: str,
    playbook_id: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> None:
    """Persist the matched (top-1) playbook ID at retrieve time.

    The column is historically named ``draft_playbook_id`` because the
    drafter used to be the only writer that knew the playbook. With the
    drafter/planner routing split, BOTH paths need this set so the
    ``Retrieved playbook`` timeline step renders after a refresh (the
    SSE merge sets it during streaming, but the DB-backed refetch
    overwrites that with NULL on the planner path).
    """
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        conn.execute(
            "UPDATE agent_sessions SET draft_playbook_id = ?, updated_at = ? "
            "WHERE ticket_id = ?",
            (playbook_id, now, ticket_id),
        )


def mark_error(
    ticket_id: str,
    step: str,
    message: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> None:
    """Persist a step failure on the session row.

    Called from ``agent_runner._record_error`` whenever classify /
    retrieve / draft / planner raises. The frontend reads these on
    refresh and renders the same red error step it shows live via the
    SSE error event — without persistence, a refresh after a crash
    would render an infinite spinner instead of the actual failure.
    """
    if step not in ("classify", "retrieve", "draft", "planner"):
        raise ValueError(f"invalid error step: {step!r}")
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        conn.execute(
            "UPDATE agent_sessions SET error_step = ?, error_message = ?, "
            "updated_at = ? WHERE ticket_id = ?",
            (step, message, now, ticket_id),
        )


def mark_routing(
    ticket_id: str,
    routing: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> None:
    """Persist which writer path this session is on ('drafter' or 'planner').

    Decided once per session, immediately after retrieval picks the top
    playbook. Used by the timeline to choose between the legacy draft step
    and the planner-skills branch — without it, a page reload mid-stream
    would render the wrong active-stage placeholder.
    """
    if routing not in ("drafter", "planner"):
        raise ValueError(f"invalid routing: {routing!r}")
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        conn.execute(
            "UPDATE agent_sessions SET routing = ?, updated_at = ? "
            "WHERE ticket_id = ?",
            (routing, now, ticket_id),
        )


def mark_planner_status(
    ticket_id: str,
    status: str,
    error: str | None = None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> None:
    """Record planner outcome on the agent_sessions row.

    Called from core.agent_runner.process_ticket after planner.run() and
    from the /actions/* endpoints after planner.resume(). Surfaces in the
    UI banner — silent planner failures are no longer possible.
    """
    init_db(db_path)
    now = _now()
    _ensure_table(ticket_id, db_path)
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        conn.execute(
            "UPDATE agent_sessions "
            "SET planner_status = ?, planner_error = ?, planner_updated_at = ?, "
            "    updated_at = ? "
            "WHERE ticket_id = ?",
            (status, error, now, now, ticket_id),
        )


def _ensure_table(ticket_id: str, db_path: Path) -> None:
    """Lazy init helper — same pattern as the existing upserts use."""
    init_db(db_path)


def mark_auto_posted(
    ticket_id: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> None:
    """Stamp ``auto_posted_at`` so the UI can tell autonomous-mode posts
    apart from human-approved ones (both look 'approved' otherwise)."""
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE agent_sessions SET auto_posted_at = ?, updated_at = ? "
            "WHERE ticket_id = ?",
            (now, now, ticket_id),
        )


