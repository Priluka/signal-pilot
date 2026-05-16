"""SQLite-backed store for operator-submitted playbook edit suggestions.

Lives alongside the feedback table in the same DB file so a single artifact
captures everything the human operator told the system.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Literal

import config


SuggestionStatus = Literal["pending", "reviewed", "merged", "dismissed"]

_VALID_STATUSES: tuple[SuggestionStatus, ...] = (
    "pending",
    "reviewed",
    "merged",
    "dismissed",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS suggestions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    playbook_id TEXT NOT NULL,
    text        TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','reviewed','merged','dismissed')),
    timestamp   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_suggestions_playbook ON suggestions(playbook_id);
CREATE INDEX IF NOT EXISTS idx_suggestions_status   ON suggestions(status);
CREATE INDEX IF NOT EXISTS idx_suggestions_ts       ON suggestions(timestamp);
"""


@dataclass
class SuggestionRecord:
    id: int
    playbook_id: str
    text: str
    status: SuggestionStatus
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


def record_suggestion(
    *,
    playbook_id: str,
    text: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> SuggestionRecord:
    if not playbook_id.strip() or not text.strip():
        raise ValueError("playbook_id and text are required")
    init_db(db_path)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO suggestions (playbook_id, text, status, timestamp) "
            "VALUES (?, ?, 'pending', ?)",
            (playbook_id, text, timestamp),
        )
        new_id = int(cursor.lastrowid or 0)
    return SuggestionRecord(
        id=new_id,
        playbook_id=playbook_id,
        text=text,
        status="pending",
        timestamp=timestamp,
    )


def list_suggestions(
    *,
    playbook_id: str | None = None,
    status: SuggestionStatus | None = None,
    limit: int = 200,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> list[SuggestionRecord]:
    init_db(db_path)
    query = "SELECT * FROM suggestions"
    clauses: list[str] = []
    params: list = []
    if playbook_id is not None:
        clauses.append("playbook_id = ?")
        params.append(playbook_id)
    if status is not None:
        if status not in _VALID_STATUSES:
            raise ValueError(f"Invalid status: {status!r}")
        clauses.append("status = ?")
        params.append(status)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    with _connect(db_path) as conn:
        rows = conn.execute(query, params).fetchall()
    return [
        SuggestionRecord(
            id=row["id"],
            playbook_id=row["playbook_id"],
            text=row["text"],
            status=row["status"],
            timestamp=row["timestamp"],
        )
        for row in rows
    ]


def update_status(
    suggestion_id: int,
    status: SuggestionStatus,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> SuggestionRecord | None:
    if status not in _VALID_STATUSES:
        raise ValueError(f"Invalid status: {status!r}")
    init_db(db_path)
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "UPDATE suggestions SET status = ? WHERE id = ?",
            (status, suggestion_id),
        )
        if cursor.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT * FROM suggestions WHERE id = ?",
            (suggestion_id,),
        ).fetchone()
    return SuggestionRecord(
        id=row["id"],
        playbook_id=row["playbook_id"],
        text=row["text"],
        status=row["status"],
        timestamp=row["timestamp"],
    )
