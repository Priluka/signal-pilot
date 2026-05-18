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


_SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_sessions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    question        TEXT NOT NULL,
    answer          TEXT NOT NULL,
    hits_json       TEXT NOT NULL,
    cited_ids_json  TEXT NOT NULL DEFAULT '[]',
    top_k           INTEGER NOT NULL,
    timestamp       TEXT NOT NULL
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


def _row_to_session(row: sqlite3.Row) -> ChatSession:
    return ChatSession(
        id=row["id"],
        question=row["question"],
        answer=row["answer"],
        hits=json.loads(row["hits_json"]),
        cited_ids=json.loads(row["cited_ids_json"]),
        top_k=row["top_k"],
        timestamp=row["timestamp"],
    )


def record_session(
    *,
    question: str,
    answer: str,
    hits: list[dict[str, Any]],
    cited_ids: list[str],
    top_k: int,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatSession:
    if not question.strip() or not answer.strip():
        raise ValueError("question and answer are required")
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
