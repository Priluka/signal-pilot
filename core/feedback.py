"""SQLite-backed feedback log.

Every approve/edit/reject from the Agent tab is written here so we can later
analyse where the drafter is right, where the playbook needs tuning, and which
clusters the retriever keeps missing.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal

import config


FeedbackStatus = Literal["approved", "edited", "rejected"]

_VALID_STATUSES: tuple[FeedbackStatus, ...] = ("approved", "edited", "rejected")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS feedback (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id   TEXT NOT NULL,
    playbook_id TEXT NOT NULL,
    draft_text  TEXT NOT NULL,
    final_text  TEXT,
    status      TEXT NOT NULL CHECK (status IN ('approved','edited','rejected')),
    timestamp   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_feedback_ticket   ON feedback(ticket_id);
CREATE INDEX IF NOT EXISTS idx_feedback_playbook ON feedback(playbook_id);
CREATE INDEX IF NOT EXISTS idx_feedback_status   ON feedback(status);
"""


@dataclass
class FeedbackRecord:
    id: int
    ticket_id: str
    playbook_id: str
    draft_text: str
    final_text: str | None
    status: FeedbackStatus
    timestamp: str


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


def record_feedback(
    *,
    ticket_id: str,
    playbook_id: str,
    draft_text: str,
    status: FeedbackStatus,
    final_text: str | None = None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> int:
    if status not in _VALID_STATUSES:
        raise ValueError(f"Invalid status: {status!r}")
    init_db(db_path)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO feedback (ticket_id, playbook_id, draft_text, final_text, status, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (ticket_id, playbook_id, draft_text, final_text, status, timestamp),
        )
        return int(cursor.lastrowid or 0)


def list_feedback(
    *,
    ticket_id: str | None = None,
    db_path: Path = config.FEEDBACK_DB_PATH,
    limit: int = 100,
) -> list[FeedbackRecord]:
    init_db(db_path)
    query = "SELECT * FROM feedback"
    params: list = []
    if ticket_id is not None:
        query += " WHERE ticket_id = ?"
        params.append(ticket_id)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with _connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [
        FeedbackRecord(
            id=row["id"],
            ticket_id=row["ticket_id"],
            playbook_id=row["playbook_id"],
            draft_text=row["draft_text"],
            final_text=row["final_text"],
            status=row["status"],
            timestamp=row["timestamp"],
        )
        for row in rows
    ]


def status_counts(db_path: Path = config.FEEDBACK_DB_PATH) -> dict[str, int]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) AS n FROM feedback GROUP BY status"
        ).fetchall()
    return {row["status"]: int(row["n"]) for row in rows}
