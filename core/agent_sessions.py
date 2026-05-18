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
    feedback_at         TEXT
);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_updated ON agent_sessions(updated_at);
"""


_TIMESTAMP_COLUMNS = ("started_at", "classified_at", "retrieved_at", "drafted_at", "feedback_at")


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
    for col in _TIMESTAMP_COLUMNS:
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
        conn.execute(
            "UPDATE agent_sessions SET classification_json = ?, classified_at = ?, "
            "retrieval_json = NULL, retrieved_at = NULL, "
            "draft_json = NULL, draft_playbook_id = NULL, drafted_at = NULL, "
            "edited_text = NULL, feedback_status = NULL, feedback_at = NULL, "
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
