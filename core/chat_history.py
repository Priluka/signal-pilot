"""SQLite-backed log of completed Chat tab Q&A sessions.

Each row is one question the operator asked + the answer Claude streamed
back + the retrieved sources + which playbook ids were cited. Sessions
are persisted at the end of streaming so they survive page refreshes and
power the history rail in the Chat tab.
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


SessionStatus = str  # 'streaming' | 'done' | 'error' — checked in app code

_SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    hits_json       TEXT NOT NULL,
    cited_ids_json  TEXT NOT NULL DEFAULT '[]',
    top_k           INTEGER NOT NULL,
    timestamp       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'streaming'
                    CHECK (status IN ('streaming','done','error')),
    error_message   TEXT
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_ts ON chat_sessions(timestamp);
"""


@dataclass
class ChatSession:
    id: int
    question: str
    answer: str
    hits: list[dict[str, Any]]
    cited_ids: list[str]
    top_k: int
    timestamp: str
    status: str = "done"
    error_message: str | None = None


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # timeout=10 lets the reader/writer threads block briefly on the SQLite
    # file lock instead of bouncing with "database is locked" — important now
    # that the chat generator thread writes while the SSE tail thread reads.
    conn = sqlite3.connect(db_path, timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _migrate_if_needed(conn: sqlite3.Connection) -> None:
    """Add the status + error_message columns if we're hitting a pre-status
    schema. Existing rows (created when sessions only landed on done) get
    status='done' so the history rail keeps showing them as completed."""
    rows = conn.execute("PRAGMA table_info(chat_sessions)").fetchall()
    cols = {row[1] for row in rows}
    if cols and "status" not in cols:
        conn.execute(
            "ALTER TABLE chat_sessions "
            "ADD COLUMN status TEXT NOT NULL DEFAULT 'streaming'"
        )
        conn.execute(
            "ALTER TABLE chat_sessions ADD COLUMN error_message TEXT"
        )
        # Pre-existing rows are by definition complete (the old code only
        # wrote on done) — mark them as such.
        conn.execute("UPDATE chat_sessions SET status = 'done' WHERE status = 'streaming'")


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)
        _migrate_if_needed(conn)


def _row_to_session(row: sqlite3.Row) -> ChatSession:
    return ChatSession(
        id=row["id"],
        question=row["question"],
        answer=row["answer"],
        hits=json.loads(row["hits_json"]),
        cited_ids=json.loads(row["cited_ids_json"]),
        top_k=row["top_k"],
        timestamp=row["timestamp"],
        status=row["status"] if "status" in row.keys() else "done",
        error_message=(
            row["error_message"] if "error_message" in row.keys() else None
        ),
    )


def create_pending_session(
    *,
    question: str,
    hits: list[dict[str, Any]],
    top_k: int,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatSession:
    """Write a fresh row with question + retrieved hits but an empty answer.

    Called as soon as the SSE handler has the retrieval result, so the row
    exists on disk before the first model chunk arrives. A page refresh
    mid-stream then has *something* to restore.
    """
    if not question.strip():
        raise ValueError("question is required")
    init_db(db_path)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO chat_sessions "
            "(question, answer, hits_json, cited_ids_json, top_k, timestamp) "
            "VALUES (?, '', ?, '[]', ?, ?)",
            (question, json.dumps(hits), top_k, timestamp),
        )
        new_id = int(cursor.lastrowid or 0)
        row = conn.execute(
            "SELECT * FROM chat_sessions WHERE id = ?", (new_id,)
        ).fetchone()
    return _row_to_session(row)


def update_session(
    session_id: int,
    *,
    answer: str | None = None,
    cited_ids: list[str] | None = None,
    status: str | None = None,
    error_message: str | None = None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatSession | None:
    """Patch an existing chat session. Any subset of fields may be omitted."""
    if status is not None and status not in ("streaming", "done", "error"):
        raise ValueError(f"invalid status: {status!r}")
    init_db(db_path)
    sets: list[str] = []
    params: list[Any] = []
    if answer is not None:
        sets.append("answer = ?")
        params.append(answer)
    if cited_ids is not None:
        sets.append("cited_ids_json = ?")
        params.append(json.dumps(cited_ids))
    if status is not None:
        sets.append("status = ?")
        params.append(status)
    if error_message is not None:
        sets.append("error_message = ?")
        params.append(error_message)
    if not sets:
        return get_session(session_id, db_path)
    params.append(session_id)
    with _connect(db_path) as conn:
        conn.execute(
            f"UPDATE chat_sessions SET {', '.join(sets)} WHERE id = ?",
            params,
        )
        row = conn.execute(
            "SELECT * FROM chat_sessions WHERE id = ?", (session_id,)
        ).fetchone()
    return _row_to_session(row) if row else None


def record_session(
    *,
    question: str,
    answer: str,
    hits: list[dict[str, Any]],
    cited_ids: list[str],
    top_k: int,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatSession:
    """One-shot create+populate. Convenience for callers that already have
    the final answer (e.g. tests)."""
    if not question.strip():
        raise ValueError("question is required")
    init_db(db_path)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO chat_sessions "
            "(question, answer, hits_json, cited_ids_json, top_k, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                question,
                answer,
                json.dumps(hits),
                json.dumps(cited_ids),
                top_k,
                timestamp,
            ),
        )
        new_id = int(cursor.lastrowid or 0)
        row = conn.execute(
            "SELECT * FROM chat_sessions WHERE id = ?", (new_id,)
        ).fetchone()
    return _row_to_session(row)


def list_sessions(
    *,
    limit: int = 200,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> list[ChatSession]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM chat_sessions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_row_to_session(r) for r in rows]


def get_session(
    session_id: int,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatSession | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM chat_sessions WHERE id = ?", (session_id,)
        ).fetchone()
    return _row_to_session(row) if row else None


def delete_session(
    session_id: int,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> bool:
    init_db(db_path)
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "DELETE FROM chat_sessions WHERE id = ?", (session_id,)
        )
    return cursor.rowcount > 0
