"""Persistent configuration for the agent's runtime behaviour.

Two SQLite tables share ``config.FEEDBACK_DB_PATH``:

* ``agent_config`` — flat key/value store for global settings (mode,
  confidence threshold, anything else operator-tunable). Keys are
  strings, values are stored as JSON so booleans / numbers round-trip
  cleanly.
* ``playbook_modes`` — per-playbook mode overrides keyed by playbook id.
  Absent rows mean ``follow the global mode``.

Three valid modes:
    shadow      — agent processes but never writes to the source system
    assisted    — agent writes a draft comment that a human must approve
    autonomous  — agent posts as final reply when confidence ≥ threshold

This module never reads its values mid-batch; the agent runner / Jira
router pull the current values at the start of each ticket.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Literal

import config


Mode = Literal["shadow", "assisted", "autonomous"]
_VALID_MODES: tuple[Mode, ...] = ("shadow", "assisted", "autonomous")

# Sensible operator defaults — the prototype boots in shadow with the
# threshold the drafter prompt already advertises as 'high confidence'.
DEFAULT_MODE: Mode = "shadow"
DEFAULT_CONFIDENCE_THRESHOLD: float = 0.60


_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS playbook_modes (
    playbook_id TEXT PRIMARY KEY,
    mode        TEXT NOT NULL
                CHECK (mode IN ('shadow','assisted','autonomous')),
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS config_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp  TEXT NOT NULL,
    field      TEXT NOT NULL,    -- 'mode' | 'threshold' | 'playbook_mode'
    target     TEXT,             -- playbook_id when field='playbook_mode'
    old_value  TEXT,
    new_value  TEXT,
    author     TEXT NOT NULL DEFAULT 'operator'
);

CREATE INDEX IF NOT EXISTS idx_config_events_ts ON config_events(timestamp);
"""


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


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


# ---------------------------------------------------------------------------
# Global config
# ---------------------------------------------------------------------------

def get_mode(db_path: Path = config.FEEDBACK_DB_PATH) -> Mode:
    val = _get("mode", db_path)
    if val in _VALID_MODES:
        return val  # type: ignore[return-value]
    return DEFAULT_MODE


def set_mode(
    mode: Mode,
    db_path: Path = config.FEEDBACK_DB_PATH,
    author: str = "operator",
) -> None:
    if mode not in _VALID_MODES:
        raise ValueError(f"mode must be one of {_VALID_MODES}, got {mode!r}")
    previous = get_mode(db_path)
    _set("mode", mode, db_path)
    if previous != mode:
        _log_config_event("mode", None, previous, mode, author, db_path)


def get_confidence_threshold(
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> float:
    val = _get("confidence_threshold", db_path)
    if val is None:
        return DEFAULT_CONFIDENCE_THRESHOLD
    try:
        return float(val)
    except (TypeError, ValueError):
        return DEFAULT_CONFIDENCE_THRESHOLD


def set_confidence_threshold(
    threshold: float,
    db_path: Path = config.FEEDBACK_DB_PATH,
    author: str = "operator",
) -> None:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("confidence_threshold must be in [0.0, 1.0]")
    previous = get_confidence_threshold(db_path)
    _set("confidence_threshold", threshold, db_path)
    # Float compare: only log if it actually moved beyond a slider-tick.
    if abs(previous - threshold) > 1e-9:
        _log_config_event(
            "threshold",
            None,
            f"{previous:.2f}",
            f"{threshold:.2f}",
            author,
            db_path,
        )


def _get(key: str, db_path: Path):
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT value FROM agent_config WHERE key = ?", (key,)
        ).fetchone()
    if row is None:
        return None
    try:
        return json.loads(row["value"])
    except (TypeError, json.JSONDecodeError):
        return row["value"]


def _set(key: str, value: object, db_path: Path) -> None:
    init_db(db_path)
    payload = json.dumps(value)
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO agent_config (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, payload),
        )


# ---------------------------------------------------------------------------
# Per-playbook modes
# ---------------------------------------------------------------------------

def get_playbook_mode(
    playbook_id: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> Mode | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT mode FROM playbook_modes WHERE playbook_id = ?",
            (playbook_id,),
        ).fetchone()
    if row is None:
        return None
    mode = row["mode"]
    return mode if mode in _VALID_MODES else None  # type: ignore[return-value]


def set_playbook_mode(
    playbook_id: str,
    mode: Mode | None,
    db_path: Path = config.FEEDBACK_DB_PATH,
    author: str = "operator",
) -> None:
    """If ``mode`` is None, drop the override so the playbook follows the
    global mode again."""
    init_db(db_path)
    previous = get_playbook_mode(playbook_id, db_path)

    if mode is None:
        with _connect(db_path) as conn:
            conn.execute(
                "DELETE FROM playbook_modes WHERE playbook_id = ?",
                (playbook_id,),
            )
        if previous is not None:
            _log_config_event(
                "playbook_mode",
                playbook_id,
                previous,
                None,  # cleared → follows global
                author,
                db_path,
            )
        return
    if mode not in _VALID_MODES:
        raise ValueError(f"mode must be one of {_VALID_MODES}, got {mode!r}")
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO playbook_modes (playbook_id, mode, updated_at) "
            "VALUES (?, ?, ?) "
            "ON CONFLICT(playbook_id) DO UPDATE SET "
            "  mode = excluded.mode, updated_at = excluded.updated_at",
            (playbook_id, mode, now),
        )
    if previous != mode:
        _log_config_event(
            "playbook_mode", playbook_id, previous, mode, author, db_path
        )


def list_playbook_modes(
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> dict[str, Mode]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT playbook_id, mode FROM playbook_modes"
        ).fetchall()
    return {r["playbook_id"]: r["mode"] for r in rows}


def effective_mode(
    playbook_id: str | None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> Mode:
    """Per-playbook override falls back to the global setting."""
    if playbook_id:
        pb_mode = get_playbook_mode(playbook_id, db_path)
        if pb_mode is not None:
            return pb_mode
    return get_mode(db_path)


# ---------------------------------------------------------------------------
# Config change audit log
# ---------------------------------------------------------------------------

def _log_config_event(
    field: str,
    target: str | None,
    old_value: object,
    new_value: object,
    author: str,
    db_path: Path,
) -> None:
    from datetime import datetime, timezone

    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.execute(
            "INSERT INTO config_events "
            "(timestamp, field, target, old_value, new_value, author) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (
                ts,
                field,
                target,
                None if old_value is None else str(old_value),
                None if new_value is None else str(new_value),
                author,
            ),
        )


def list_config_events(
    limit: int = 500,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> list[dict]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, timestamp, field, target, old_value, new_value, author "
            "FROM config_events ORDER BY timestamp DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in rows]
