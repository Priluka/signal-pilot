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

import re
import sqlite3
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator, Literal

import config


SuggestionStatus = Literal["pending", "accepted", "rejected"]
SuggestionType = Literal["edit", "add", "remove"]

_VALID_STATUSES: tuple[SuggestionStatus, ...] = ("pending", "accepted", "rejected")
_VALID_TYPES: tuple[SuggestionType, ...] = ("edit", "add", "remove")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS suggestions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    playbook_id TEXT NOT NULL,
    section     TEXT NOT NULL,
    step_number INTEGER,
    old_text    TEXT NOT NULL DEFAULT '',
    new_text    TEXT NOT NULL DEFAULT '',
    author      TEXT NOT NULL DEFAULT 'anonymous',
    status      TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','accepted','rejected')),
    timestamp   TEXT NOT NULL,
    decided_at  TEXT,
    type        TEXT NOT NULL DEFAULT 'edit'
                CHECK (type IN ('edit','add','remove')),
    position    TEXT
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
    decided_at: str | None = None
    type: SuggestionType = "edit"
    position: str | None = None


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
    """Bring the suggestions table forward through any prior schemas.

    Migration policy: destructive for the very-old prototype shape (no
    user data to preserve there); additive for column adds that came later.
    """
    rows = conn.execute("PRAGMA table_info(suggestions)").fetchall()
    cols = {row[1] for row in rows}
    if cols and "old_text" not in cols:
        # The pre-history shape only had ``text`` + a different status set —
        # drop and rebuild rather than try to preserve.
        conn.execute("DROP TABLE suggestions")
        return
    if cols and "decided_at" not in cols:
        # Added so the Activity Log can timestamp accept/reject events at
        # their actual decision time, not at suggestion creation time.
        conn.execute("ALTER TABLE suggestions ADD COLUMN decided_at TEXT")
    if cols and "type" not in cols:
        # Suggestion type: 'edit' was the original behaviour; 'add' and
        # 'remove' came later. CHECK constraint can't be added via ALTER
        # — we rely on the application layer to validate inputs.
        conn.execute(
            "ALTER TABLE suggestions ADD COLUMN type TEXT NOT NULL DEFAULT 'edit'"
        )
    if cols and "position" not in cols:
        # Only used by type='add'. Format: 'end' for tail-append, or
        # 'after:N' (1-indexed step / bullet) for in-list insertion.
        conn.execute("ALTER TABLE suggestions ADD COLUMN position TEXT")


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        _migrate_if_needed(conn)
        conn.executescript(_SCHEMA)


def _row_to_record(row: sqlite3.Row) -> SuggestionRecord:
    keys = row.keys()
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
        decided_at=row["decided_at"] if "decided_at" in keys else None,
        type=row["type"] if "type" in keys else "edit",
        position=row["position"] if "position" in keys else None,
    )


def record_suggestion(
    *,
    playbook_id: str,
    section: str,
    step_number: int | None,
    old_text: str,
    new_text: str,
    author: str = "anonymous",
    type: SuggestionType = "edit",
    position: str | None = None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> SuggestionRecord:
    if not playbook_id.strip():
        raise ValueError("playbook_id is required")
    if type not in _VALID_TYPES:
        raise ValueError(f"type must be one of {_VALID_TYPES}, got {type!r}")

    # Per-type field requirements. 'edit' is the historical contract;
    # 'add' needs only the new text (and optionally a position); 'remove'
    # needs only the old text. Anything missing here is a contract bug at
    # the API layer and surfaces as a 422 there.
    if type == "edit":
        if not old_text or not new_text.strip():
            raise ValueError("edit suggestions need both old_text and new_text")
    elif type == "add":
        if not new_text.strip():
            raise ValueError("add suggestions need new_text")
    elif type == "remove":
        if not old_text.strip():
            raise ValueError("remove suggestions need old_text")

    init_db(db_path)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO suggestions "
            "(playbook_id, section, step_number, old_text, new_text, author, "
            " status, timestamp, type, position) "
            "VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)",
            (
                playbook_id,
                section,
                step_number,
                old_text,
                new_text,
                author or "anonymous",
                timestamp,
                type,
                position,
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
    # ``decided_at`` is only stamped for terminal statuses — moving a row
    # back to pending (which we don't currently support, but might) would
    # otherwise lose the audit trail of the previous decision.
    now = datetime.now(timezone.utc).isoformat() if status != "pending" else None
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "UPDATE suggestions SET status = ?, decided_at = ? WHERE id = ?",
            (status, now, suggestion_id),
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
    verb = {"edit": "update", "add": "add to", "remove": "remove from"}[record.type]
    return f"suggestion #{record.id} accepted: {verb} {section} in {record.playbook_id}"


# ---------------------------------------------------------------------------
# Section-aware markdown rewriting
# ---------------------------------------------------------------------------

# Section identifier (as stored in `suggestions.section`) → ``## Heading``
# in the playbook markdown. Anything not here falls through to a literal
# text-find/replace, which is only valid for the 'edit' type.
_SECTION_HEADINGS: dict[str, str] = {
    "when_applies": "## When this applies",
    "resolution_flow": "## Typical resolution flow",
    # The frontend has historically tagged step edits as 'resolution_step';
    # treat it as an alias of the resolution_flow section for add/remove.
    "resolution_step": "## Typical resolution flow",
}

_NUMBERED_RE = re.compile(r"^(\s*)(\d+)\.\s+(.*\S.*)$")
_BULLET_RE = re.compile(r"^(\s*-\s+)(.*\S.*)$")


def _section_bounds(lines: list[str], heading: str) -> tuple[int, int] | None:
    """Find the line range belonging to ``heading``.

    Returns (start, end): start = first line after the heading; end = first
    next-section heading line (exclusive) or len(lines)."""
    start = None
    for i, line in enumerate(lines):
        if line.strip() == heading:
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return start, end


def _parse_position(position: str | None) -> tuple[str, int | None]:
    """Return (kind, n) for a position spec. kind ∈ {'end', 'after'}."""
    if not position or position == "end":
        return "end", None
    if position.startswith("after:"):
        try:
            return "after", int(position.split(":", 1)[1])
        except ValueError:
            pass
    raise SuggestionError(422, f"Invalid position {position!r}")


def _apply_add(content: str, record: SuggestionRecord) -> str:
    heading = _SECTION_HEADINGS.get(record.section)
    if heading is None:
        raise SuggestionError(
            422, f"'add' is not supported for section {record.section!r}"
        )
    lines = content.split("\n")
    bounds = _section_bounds(lines, heading)
    if bounds is None:
        raise SuggestionError(
            404, f"Section {heading!r} not found in playbook"
        )
    start, end = bounds
    pos_kind, pos_n = _parse_position(record.position)

    if heading == "## Typical resolution flow":
        return _insert_numbered(lines, start, end, pos_kind, pos_n, record.new_text)
    return _insert_bullet(lines, start, end, pos_kind, pos_n, record.new_text)


def _insert_numbered(
    lines: list[str],
    start: int,
    end: int,
    pos_kind: str,
    pos_n: int | None,
    new_text: str,
) -> str:
    """Insert ``new_text`` into a numbered list and renumber the whole list."""
    items: list[tuple[int, str]] = []  # (line_index_in_lines, text)
    for i in range(start, end):
        m = _NUMBERED_RE.match(lines[i])
        if m:
            items.append((i, m.group(3)))

    new_step_text = new_text.strip()
    if pos_kind == "end":
        items.append((-1, new_step_text))
    else:
        assert pos_n is not None
        if pos_n < 1 or pos_n > len(items):
            raise SuggestionError(
                422, f"after:{pos_n} is out of range — list has {len(items)} steps"
            )
        items.insert(pos_n, (-1, new_step_text))

    # Re-emit the section: keep the heading and any leading blank lines,
    # rewrite the numbered list, preserve any non-list trailing lines.
    out = list(lines[:start])
    # Replicate any blank lines immediately after the heading.
    cursor = start
    while cursor < end and not lines[cursor].strip():
        out.append(lines[cursor])
        cursor += 1
    # Emit renumbered list.
    for n, (_, text) in enumerate(items, start=1):
        out.append(f"{n}. {text}")
    # Carry over any post-list content within the section (rare, but the
    # 'Typical resolution flow' section sometimes has trailing prose).
    in_list_block = True
    for j in range(cursor, end):
        if _NUMBERED_RE.match(lines[j]):
            in_list_block = False
            continue
        if in_list_block and not lines[j].strip():
            continue
        in_list_block = False
        out.append(lines[j])
    out.extend(lines[end:])
    return "\n".join(out)


def _insert_bullet(
    lines: list[str],
    start: int,
    end: int,
    pos_kind: str,
    pos_n: int | None,
    new_text: str,
) -> str:
    bullet_indices: list[int] = [
        i for i in range(start, end) if _BULLET_RE.match(lines[i])
    ]
    if pos_kind == "end":
        insert_at = bullet_indices[-1] + 1 if bullet_indices else start
    else:
        assert pos_n is not None
        if pos_n < 1 or pos_n > len(bullet_indices):
            raise SuggestionError(
                422,
                f"after:{pos_n} is out of range — list has {len(bullet_indices)} bullets",
            )
        insert_at = bullet_indices[pos_n - 1] + 1
    new_line = f"- {new_text.strip()}"
    return "\n".join(lines[:insert_at] + [new_line] + lines[insert_at:])


def _apply_remove(content: str, record: SuggestionRecord) -> str:
    """Delete the line containing ``old_text`` from the relevant section
    and, for numbered lists, renumber the remaining items."""
    heading = _SECTION_HEADINGS.get(record.section)
    lines = content.split("\n")

    target = record.old_text.rstrip("\n")
    matches = [i for i, line in enumerate(lines) if line == target]
    if not matches:
        # Fall back to a substring match — the old_text may include the
        # raw bullet/number prefix and trail spaces from the original line.
        matches = [
            i for i, line in enumerate(lines)
            if target and target.strip() and target in line and line.strip().endswith(target.strip())
        ]
    if not matches:
        raise SuggestionError(
            409,
            "Target line not found — it may have been edited since the suggestion was submitted.",
        )
    if len(matches) > 1:
        raise SuggestionError(
            409,
            f"Target line appears {len(matches)} times — cannot disambiguate.",
        )
    del lines[matches[0]]

    if heading == "## Typical resolution flow":
        bounds = _section_bounds(lines, heading)
        if bounds is not None:
            start, end = bounds
            n = 1
            for i in range(start, end):
                m = _NUMBERED_RE.match(lines[i])
                if m:
                    lines[i] = f"{m.group(1)}{n}. {m.group(3)}"
                    n += 1
    return "\n".join(lines)


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
    if record.type == "edit" and record.old_text == record.new_text:
        raise SuggestionError(422, "Suggestion contains no change")

    path = playbook_path_lookup(record.playbook_id)
    if path is None or not path.exists():
        raise SuggestionError(
            404, f"Playbook file for {record.playbook_id!r} not found on disk"
        )

    content = path.read_text(encoding="utf-8")

    if record.type == "edit":
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
    elif record.type == "add":
        new_content = _apply_add(content, record)
    elif record.type == "remove":
        new_content = _apply_remove(content, record)
    else:
        raise SuggestionError(422, f"Unknown suggestion type {record.type!r}")

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
