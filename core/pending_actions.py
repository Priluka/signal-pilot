"""Pending-actions table — minimal HITL state for the planner's pause.

When the planner hits a write skill that needs human approval it can't
just block — Anthropic API calls aren't free and the request that
triggered the run is already long-running. So we **snapshot the loop
state** (messages so far, which tool_use we paused on, iteration number)
into this table, return ``awaiting_approval`` to the caller, and let the
frontend show the operator what's pending.

When the operator clicks Approve or Reject, we ``load()`` the snapshot,
execute (or fake-reject) the skill, and call ``planner.run(..., resume_action_id=...)``
to continue from where we stopped.

The table is intentionally minimal (per ``AGENT_IMPLEMENTATION.md`` §11):
no audit history, no decided_by, no analytics. Rows are **deleted** after
the action is approved/rejected — this is loop state, not an audit log.
That comes in a v2 ``agent_actions`` table when we go to production.
"""
from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import config


# Same SQLite file as agent_sessions / agent_config — one db, multiple
# tables. Keeps deploy simple (one file to back up) and joins cheap.
_DB_PATH: Path = config.FEEDBACK_DB_PATH


_SCHEMA = """
CREATE TABLE IF NOT EXISTS pending_actions (
    id            TEXT PRIMARY KEY,
    ticket_id     TEXT NOT NULL,
    playbook_id   TEXT NOT NULL,
    skill_name    TEXT NOT NULL,
    skill_input   TEXT NOT NULL,           -- JSON
    messages_blob TEXT NOT NULL,           -- JSON list of Anthropic messages
    tool_use_id   TEXT NOT NULL,
    iteration     INTEGER NOT NULL,
    mode          TEXT NOT NULL,
    created_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS pending_actions_by_ticket
    ON pending_actions(ticket_id);
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
    """Create the table if it doesn't exist. Safe to call repeatedly."""
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


@dataclass
class PendingAction:
    """One paused tool_use waiting for operator decision."""

    id: str
    ticket_id: str
    playbook_id: str
    skill_name: str
    skill_input: dict[str, Any]
    messages_blob: list[dict[str, Any]]
    tool_use_id: str
    iteration: int
    mode: str
    created_at: str = field(default_factory=lambda: _now())


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _row_to_action(row: sqlite3.Row) -> PendingAction:
    return PendingAction(
        id=row["id"],
        ticket_id=row["ticket_id"],
        playbook_id=row["playbook_id"],
        skill_name=row["skill_name"],
        skill_input=json.loads(row["skill_input"]),
        messages_blob=json.loads(row["messages_blob"]),
        tool_use_id=row["tool_use_id"],
        iteration=int(row["iteration"]),
        mode=row["mode"],
        created_at=row["created_at"],
    )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def save(
    *,
    ticket_id: str,
    playbook_id: str,
    skill_name: str,
    skill_input: dict[str, Any],
    messages: list[dict[str, Any]],
    tool_use_id: str,
    iteration: int,
    mode: str,
    db_path: Path = _DB_PATH,
) -> str:
    """Persist a pending action; return its generated UUID id."""
    init_db(db_path)
    action_id = str(uuid.uuid4())
    with _connect(db_path) as conn:
        conn.execute(
            """INSERT INTO pending_actions
               (id, ticket_id, playbook_id, skill_name, skill_input,
                messages_blob, tool_use_id, iteration, mode, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                action_id,
                ticket_id,
                playbook_id,
                skill_name,
                json.dumps(skill_input),
                json.dumps(messages),
                tool_use_id,
                iteration,
                mode,
                _now(),
            ),
        )
    return action_id


def get(action_id: str, db_path: Path = _DB_PATH) -> PendingAction | None:
    """Load one action by id, or None if not found / already resolved."""
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM pending_actions WHERE id = ?",
            (action_id,),
        ).fetchone()
    return _row_to_action(row) if row else None


def list_for_ticket(
    ticket_id: str,
    db_path: Path = _DB_PATH,
) -> list[PendingAction]:
    """All pending actions for one ticket, oldest first."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM pending_actions WHERE ticket_id = ? ORDER BY created_at",
            (ticket_id,),
        ).fetchall()
    return [_row_to_action(r) for r in rows]


def list_all(db_path: Path = _DB_PATH) -> list[PendingAction]:
    """All pending actions across the workspace, oldest first."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM pending_actions ORDER BY created_at"
        ).fetchall()
    return [_row_to_action(r) for r in rows]


def delete(action_id: str, db_path: Path = _DB_PATH) -> None:
    """Drop a row after the operator decides (approve or reject)."""
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM pending_actions WHERE id = ?", (action_id,))


def count_for_ticket(ticket_id: str, db_path: Path = _DB_PATH) -> int:
    """Cheap count for sidebar / inbox badge."""
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM pending_actions WHERE ticket_id = ?",
            (ticket_id,),
        ).fetchone()
    return int(row["c"]) if row else 0
