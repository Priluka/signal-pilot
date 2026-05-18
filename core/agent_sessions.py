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
    updated_at          TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_updated ON agent_sessions(updated_at);
"""


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


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


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


def upsert_classification(
    ticket_id: str,
    classification: dict[str, Any],
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> AgentSessionRecord:
    init_db(db_path)
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        # New classification invalidates everything downstream (retrieval was
        # tied to a previous classification, draft was tied to that retrieval).
        conn.execute(
            "UPDATE agent_sessions SET classification_json = ?, retrieval_json = NULL, "
            "draft_json = NULL, draft_playbook_id = NULL, edited_text = NULL, "
            "feedback_status = NULL, updated_at = ? WHERE ticket_id = ?",
            (json.dumps(classification), _now(), ticket_id),
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
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        # New retrieval invalidates the existing draft / edits / feedback —
        # those were tied to a specific playbook list that may now differ.
        conn.execute(
            "UPDATE agent_sessions SET retrieval_json = ?, draft_json = NULL, "
            "draft_playbook_id = NULL, edited_text = NULL, feedback_status = NULL, "
            "updated_at = ? WHERE ticket_id = ?",
            (json.dumps(retrieval), _now(), ticket_id),
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
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        # New draft resets edits/feedback that referenced the previous one.
        conn.execute(
            "UPDATE agent_sessions SET draft_json = ?, draft_playbook_id = ?, "
            "edited_text = NULL, feedback_status = NULL, updated_at = ? "
            "WHERE ticket_id = ?",
            (json.dumps(draft), playbook_id, _now(), ticket_id),
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
    with _connect(db_path) as conn:
        _ensure_row(conn, ticket_id)
        conn.execute(
            "UPDATE agent_sessions SET feedback_status = ?, edited_text = ?, "
            "updated_at = ? WHERE ticket_id = ?",
            (status, edited_text, _now(), ticket_id),
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
