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
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatSession | None:
    """Patch an existing chat session. Used for checkpointing during streaming
    and for the final write at the ``done`` event. Either field may be
    omitted to update only the other one."""
    init_db(db_path)
    sets: list[str] = []
    params: list[Any] = []
    if answer is not None:
        sets.append("answer = ?")
        params.append(answer)
    if cited_ids is not None:
        sets.append("cited_ids_json = ?")
        params.append(json.dumps(cited_ids))
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
