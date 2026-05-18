"""SQLite-backed store for operator playbook edit suggestions.

Each suggestion proposes replacing some ``old_text`` chunk inside a playbook
markdown file with ``new_text``. A reviewer can later accept (which rewrites
the file on disk + creates a git commit) or reject. Reject is a state change
only — the markdown is never touched.

The ``section`` field is a free-form display label (e.g. ``resolution_step``,
``when_applies``, ``typical_action_what``) and ``step_number`` is an optional
1-based index so the SuggestionsPage can render a precise human label.
Neither field participates in the accept logic — replacement is driven
purely by the ``old_text`` substring, which must appear in the playbook
exactly once.
"""
from __future__ import annotations

import sqlite3
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator, Literal

import config


SuggestionStatus = Literal["pending", "accepted", "rejected"]

_VALID_STATUSES: tuple[SuggestionStatus, ...] = ("pending", "accepted", "rejected")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS suggestions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    playbook_id TEXT NOT NULL,
    section     TEXT NOT NULL,
    step_number INTEGER,
    old_text    TEXT NOT NULL,
    new_text    TEXT NOT NULL,
    author      TEXT NOT NULL DEFAULT 'anonymous',
    status      TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','accepted','rejected')),
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
    section: str
    step_number: int | None
    old_text: str
    new_text: str
    author: str
    status: SuggestionStatus
    timestamp: str


class SuggestionError(Exception):
    """Domain error translated to an HTTP response at the router boundary."""

    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


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
    """Drop the legacy single-text-column schema if we encounter it.

    The previous shape stored only ``text`` per row with statuses
    pending|reviewed|merged|dismissed. Both data and constraints diverge
    from the new shape, and the only rows in the wild were prototype tests
    — drop the table and start fresh.
    """
    rows = conn.execute("PRAGMA table_info(suggestions)").fetchall()
    cols = {row[1] for row in rows}
    if cols and "old_text" not in cols:
        conn.execute("DROP TABLE suggestions")


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        _migrate_if_needed(conn)
        conn.executescript(_SCHEMA)


def _row_to_record(row: sqlite3.Row) -> SuggestionRecord:
    return SuggestionRecord(
        id=row["id"],
        playbook_id=row["playbook_id"],
        section=row["section"],
        step_number=row["step_number"],
        old_text=row["old_text"],
        new_text=row["new_text"],
        author=row["author"],
        status=row["status"],
        timestamp=row["timestamp"],
    )


def record_suggestion(
    *,
    playbook_id: str,
    section: str,
    step_number: int | None,
    old_text: str,
    new_text: str,
    author: str = "anonymous",
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> SuggestionRecord:
    if not playbook_id.strip() or not old_text or not new_text.strip():
        raise ValueError("playbook_id, old_text, and new_text are required")
    init_db(db_path)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO suggestions "
            "(playbook_id, section, step_number, old_text, new_text, author, status, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)",
            (
                playbook_id,
                section,
                step_number,
                old_text,
                new_text,
                author or "anonymous",
                timestamp,
            ),
        )
        new_id = int(cursor.lastrowid or 0)
        row = conn.execute(
            "SELECT * FROM suggestions WHERE id = ?", (new_id,)
        ).fetchone()
    return _row_to_record(row)


def get_suggestion(
    suggestion_id: int,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> SuggestionRecord | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM suggestions WHERE id = ?", (suggestion_id,)
        ).fetchone()
    return _row_to_record(row) if row else None


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
    return [_row_to_record(r) for r in rows]


def _set_status(
    suggestion_id: int,
    status: SuggestionStatus,
    db_path: Path,
) -> SuggestionRecord | None:
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "UPDATE suggestions SET status = ? WHERE id = ?",
            (status, suggestion_id),
        )
        if cursor.rowcount == 0:
            return None
        row = conn.execute(
            "SELECT * FROM suggestions WHERE id = ?", (suggestion_id,)
        ).fetchone()
    return _row_to_record(row) if row else None


def _commit_message(record: SuggestionRecord) -> str:
    section = record.section
    if record.step_number is not None:
        section = f"{section} #{record.step_number}"
    return f"suggestion #{record.id} accepted: update {section} in {record.playbook_id}"


def accept_suggestion(
    suggestion_id: int,
    *,
    playbook_path_lookup: Callable[[str], Path | None],
    repo_root: Path = config.ROOT_DIR,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> SuggestionRecord:
    record = get_suggestion(suggestion_id, db_path)
    if record is None:
        raise SuggestionError(404, f"Suggestion {suggestion_id} not found")
    if record.status != "pending":
        raise SuggestionError(
            409, f"Suggestion {suggestion_id} already {record.status}"
        )
    if record.old_text == record.new_text:
        raise SuggestionError(422, "Suggestion contains no change")

    path = playbook_path_lookup(record.playbook_id)
    if path is None or not path.exists():
        raise SuggestionError(
            404, f"Playbook file for {record.playbook_id!r} not found on disk"
        )

    content = path.read_text(encoding="utf-8")
    occurrences = content.count(record.old_text)
    if occurrences == 0:
        raise SuggestionError(
            409,
            "Original text not found in playbook — it may have been edited since "
            "the suggestion was submitted.",
        )
    if occurrences > 1:
        raise SuggestionError(
            409,
            f"Original text appears {occurrences} times in the playbook — cannot "
            "disambiguate which occurrence to replace.",
        )

    new_content = content.replace(record.old_text, record.new_text, 1)
    path.write_text(new_content, encoding="utf-8")

    rel = path.relative_to(repo_root)
    try:
        subprocess.run(
            ["git", "add", str(rel)],
            cwd=repo_root,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", _commit_message(record)],
            cwd=repo_root,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        # Roll the file back so we don't leave a dirty working tree from a
        # half-applied accept.
        path.write_text(content, encoding="utf-8")
        stderr = exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc)
        raise SuggestionError(500, f"git commit failed: {stderr.strip()}") from exc

    updated = _set_status(suggestion_id, "accepted", db_path)
    assert updated is not None
    return updated


def reject_suggestion(
    suggestion_id: int,
    *,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> SuggestionRecord:
    record = get_suggestion(suggestion_id, db_path)
    if record is None:
        raise SuggestionError(404, f"Suggestion {suggestion_id} not found")
    if record.status != "pending":
        raise SuggestionError(
            409, f"Suggestion {suggestion_id} already {record.status}"
        )
    updated = _set_status(suggestion_id, "rejected", db_path)
    assert updated is not None
    return updated
