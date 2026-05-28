"""Append-only audit log for every executed skill.

``pending_actions`` is loop-state — rows are deleted the moment the
operator decides. That's the right behaviour for the planner but the
WRONG behaviour for compliance: SOC 2 / GDPR auditors will ask "who
approved what, when, with what result" and we need a permanent record.

This table fills that gap. One row per terminal skill outcome:

- ``approved`` — operator OK'd, skill executed, result captured
- ``rejected`` — operator refused, no execution
- ``auto``     — read skill or autonomous-write, no operator involved
- ``shadow``   — shadow mode, no real execution

Rows are NEVER deleted. The /actions/history endpoint exposes a slice
for the UI; downstream BI tooling pulls direct from SQLite.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import config


_DB_PATH: Path = config.FEEDBACK_DB_PATH


_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_actions_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id       TEXT NOT NULL,
    playbook_id     TEXT NOT NULL,
    skill_name      TEXT NOT NULL,
    skill_input     TEXT NOT NULL,          -- JSON
    outcome         TEXT NOT NULL,          -- approved|rejected|auto|shadow
    ok              INTEGER NOT NULL,       -- 1/0
    result_data     TEXT,                   -- JSON, when ok=1
    error           TEXT,                   -- when ok=0
    decided_by      TEXT,                   -- operator id (None for auto/shadow)
    mode            TEXT NOT NULL,
    iteration       INTEGER NOT NULL,
    decided_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS agent_actions_history_by_ticket
    ON agent_actions_history(ticket_id);
CREATE INDEX IF NOT EXISTS agent_actions_history_by_time
    ON agent_actions_history(decided_at);
"""


@contextmanager
def _connect(db_path: Path = _DB_PATH) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path = _DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class AuditEntry:
    id: int
    ticket_id: str
    playbook_id: str
    skill_name: str
    skill_input: dict[str, Any]
    outcome: str
    ok: bool
    result_data: dict[str, Any] | None
    error: str | None
    decided_by: str | None
    mode: str
    iteration: int
    decided_at: str = field(default_factory=_now)


def _row_to_entry(row: sqlite3.Row) -> AuditEntry:
    return AuditEntry(
        id=int(row["id"]),
        ticket_id=row["ticket_id"],
        playbook_id=row["playbook_id"],
        skill_name=row["skill_name"],
        skill_input=json.loads(row["skill_input"]) if row["skill_input"] else {},
        outcome=row["outcome"],
        ok=bool(row["ok"]),
        result_data=json.loads(row["result_data"]) if row["result_data"] else None,
        error=row["error"],
        decided_by=row["decided_by"],
        mode=row["mode"],
        iteration=int(row["iteration"]),
        decided_at=row["decided_at"],
    )


def record(
    *,
    ticket_id: str,
    playbook_id: str,
    skill_name: str,
    skill_input: dict[str, Any],
    outcome: str,
    ok: bool,
    result_data: dict[str, Any] | None = None,
    error: str | None = None,
    decided_by: str | None = None,
    mode: str,
    iteration: int,
    db_path: Path = _DB_PATH,
) -> int:
    """Append one row. Returns the row id. Never deletes anything."""
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute(
            """INSERT INTO agent_actions_history
               (ticket_id, playbook_id, skill_name, skill_input, outcome,
                ok, result_data, error, decided_by, mode, iteration, decided_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                ticket_id,
                playbook_id,
                skill_name,
                json.dumps(skill_input, default=str),
                outcome,
                1 if ok else 0,
                json.dumps(result_data, default=str) if result_data is not None else None,
                error,
                decided_by,
                mode,
                iteration,
                _now(),
            ),
        )
        return int(cur.lastrowid or 0)


def list_for_ticket(
    ticket_id: str,
    db_path: Path = _DB_PATH,
) -> list[AuditEntry]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM agent_actions_history "
            "WHERE ticket_id = ? ORDER BY decided_at DESC",
            (ticket_id,),
        ).fetchall()
    return [_row_to_entry(r) for r in rows]


def list_recent(
    limit: int = 200,
    db_path: Path = _DB_PATH,
) -> list[AuditEntry]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM agent_actions_history "
            "ORDER BY decided_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [_row_to_entry(r) for r in rows]
