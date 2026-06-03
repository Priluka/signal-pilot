"""Multi-turn chat persistence — threads + turns.

Replaces the single-Q-single-A shape of ``core.chat_history`` with a
proper conversation model:

    chat_threads (id, title, created_at, updated_at)
        ↓ 1..N
    chat_turns (id, thread_id, turn_index, user_text,
                final_assistant_text, trace_json, events_json,
                sources_json, citation_index_json, status,
                error_message, created_at, updated_at)

Each turn is one operator-perceived exchange: the user sent ``user_text``,
the agent ran a (possibly multi-iteration) tool_use loop, and produced
``final_assistant_text``. ``trace_json`` carries the FULL Anthropic-shaped
message history for that turn — text blocks, tool_use blocks, and the
matching tool_result blocks — so the next turn can feed Claude the
complete conversation context.

Existing ``chat_sessions`` rows are migrated on first init: each becomes
a single-turn thread. The trace for migrated turns contains only the
final text (we don't have the original tool_use blocks), which is enough
for resuming a conversation but loses the per-skill execution detail.
The original ``chat_sessions`` table is left in place during the
transition so legacy code paths keep working.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

import config


# ---------------------------------------------------------------------------
# Schema + connection
# ---------------------------------------------------------------------------


_SCHEMA = """
CREATE TABLE IF NOT EXISTS chat_threads (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chat_threads_updated
    ON chat_threads(updated_at DESC);

CREATE TABLE IF NOT EXISTS chat_turns (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id            INTEGER NOT NULL,
    turn_index           INTEGER NOT NULL,
    user_text            TEXT NOT NULL,
    final_assistant_text TEXT NOT NULL DEFAULT '',
    -- ``trace_json`` is the full Anthropic-shaped messages array
    -- for this turn (user + assistant + tool_result blocks across
    -- inner iterations of the tool_use loop). The next turn's
    -- agent call concatenates trace_json from every prior turn so
    -- Claude sees the complete conversation history.
    trace_json           TEXT NOT NULL DEFAULT '[]',
    -- ``events_json`` is the UI replay timeline: skill_executing /
    -- skill_executed / composing entries the agent emitted for THIS
    -- turn. Used to rebuild the AgenticSkillTimeline on refresh.
    events_json          TEXT NOT NULL DEFAULT '[]',
    -- Per-turn retrieved playbook hits (top_k). Each turn may retrieve
    -- afresh as the conversation topic shifts; storing per-turn means
    -- the sidebar / detail view can show what context THIS turn ran
    -- against.
    sources_json         TEXT NOT NULL DEFAULT '[]',
    -- Per-turn resolved citation index ([id] mentions → playbook
    -- metadata), computed at done.
    citation_index_json  TEXT NOT NULL DEFAULT '[]',
    -- Per-turn Anthropic usage accumulated across the inner-iteration
    -- tool_use loop. Shape: {"input_tokens": int, "output_tokens": int,
    -- "cost_usd": float}. Stored as JSON so we can extend later
    -- (cache hits, thinking-budget tokens) without another migration.
    usage_json           TEXT NOT NULL DEFAULT '{}',
    status               TEXT NOT NULL DEFAULT 'streaming'
                         CHECK (status IN ('streaming','done','error')),
    error_message        TEXT,
    created_at           TEXT NOT NULL,
    updated_at           TEXT NOT NULL,
    FOREIGN KEY (thread_id) REFERENCES chat_threads(id) ON DELETE CASCADE,
    UNIQUE (thread_id, turn_index)
);
CREATE INDEX IF NOT EXISTS idx_chat_turns_thread
    ON chat_turns(thread_id, turn_index);
"""


@contextmanager
def _connect(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30.0)
    # WAL mode lets readers and one writer proceed concurrently —
    # essential when concurrent turn daemons + SSE tails + HTTP
    # handlers all hit chat_turns. ``synchronous=NORMAL`` is the
    # WAL-recommended pairing (safe across crashes, faster than FULL).
    # ``busy_timeout`` is a belt-and-braces backstop: if a writer
    # holds the lock briefly, SQLite waits instead of throwing
    # ``database is locked``.
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=10000")
    conn.execute("PRAGMA foreign_keys=ON")  # required for ON DELETE CASCADE
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# Phase 13.4 — versioned migrations. Each migration is a function
# that takes a connection and applies its delta. We track the highest
# applied version in a ``schema_versions`` table. On boot we walk the
# pending migrations in numeric order. Idempotent — re-running init_db
# is safe.
#
# To add a new migration:
#   1. Define a function ``_migration_NNN_short_name(conn)`` below.
#   2. Append ``(NNN, "short_name", _migration_NNN_short_name)`` to
#      ``_MIGRATIONS`` in order.
#   3. Don't renumber existing entries — versions are immutable once
#      shipped.


def _migration_001_sessions_to_threads(conn: sqlite3.Connection) -> None:
    _migrate_sessions_to_threads(conn)


def _migration_002_chat_turns_usage_json(conn: sqlite3.Connection) -> None:
    cur = conn.execute("PRAGMA table_info(chat_turns)")
    cols = {row[1] for row in cur.fetchall()}
    if "usage_json" not in cols:
        conn.execute(
            "ALTER TABLE chat_turns ADD COLUMN usage_json TEXT NOT NULL "
            "DEFAULT '{}'"
        )


def _migration_003_chat_threads_deleted_at(conn: sqlite3.Connection) -> None:
    cur = conn.execute("PRAGMA table_info(chat_threads)")
    cols = {row[1] for row in cur.fetchall()}
    if "deleted_at" not in cols:
        conn.execute(
            "ALTER TABLE chat_threads ADD COLUMN deleted_at TEXT"
        )
        # Index helps the soft-delete-aware list query.
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_chat_threads_deleted "
            "ON chat_threads(deleted_at)"
        )


_MIGRATIONS: list[tuple[int, str, Callable[[sqlite3.Connection], None]]] = [
    (1, "sessions_to_threads", _migration_001_sessions_to_threads),
    (2, "chat_turns_usage_json", _migration_002_chat_turns_usage_json),
    (3, "chat_threads_deleted_at", _migration_003_chat_threads_deleted_at),
]


def _run_pending_migrations(conn: sqlite3.Connection) -> list[int]:
    """Apply migrations whose version is greater than the current
    schema_versions max. Returns the list of versions newly applied
    so init_db can log them. Re-runs are no-ops."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_versions ("
        "  version INTEGER PRIMARY KEY,"
        "  name TEXT NOT NULL,"
        "  applied_at TEXT NOT NULL"
        ")"
    )
    row = conn.execute(
        "SELECT COALESCE(MAX(version), 0) AS v FROM schema_versions"
    ).fetchone()
    current = int(row["v"]) if row else 0
    applied: list[int] = []
    for version, name, fn in _MIGRATIONS:
        if version <= current:
            continue
        fn(conn)
        conn.execute(
            "INSERT INTO schema_versions (version, name, applied_at) "
            "VALUES (?, ?, ?)",
            (version, name, _now()),
        )
        applied.append(version)
    return applied


def init_db(db_path: Path = config.FEEDBACK_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)
        _run_pending_migrations(conn)


def purge_threads_older_than(
    days: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> int:
    """Phase 12.9 + 13.7 — retention sweep. Hard-deletes threads that
    are EITHER older than ``days`` days OR soft-deleted earlier.
    Soft-deleted threads with ``deleted_at`` past the cutoff get
    permanently removed; live threads past the cutoff are also
    removed. Returns the number of deleted threads. FK cascade
    removes every turn underneath."""
    if days <= 0:
        raise ValueError("days must be positive")
    init_db(db_path)
    from datetime import timedelta

    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM chat_threads "
            "WHERE updated_at < ? OR "
            "(deleted_at IS NOT NULL AND deleted_at < ?)",
            (cutoff, cutoff),
        )
        return cur.rowcount or 0


def recover_orphan_streaming_turns(
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> int:
    """Phase 11.3 — sweep any turn rows left in ``status='streaming'``
    from a previous backend instance that crashed or was killed
    mid-flight. Without this, the UI would render them as 'still
    running' forever and the sidebar would show stale spinners.

    Marks each such row as ``status='error'`` with a clear marker
    message so the operator can distinguish post-crash debris from
    real operator-side errors. Returns the count of recovered rows
    so the lifespan hook can log it on boot.
    """
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        cur = conn.execute(
            "UPDATE chat_turns SET status = 'error', "
            "error_message = 'Process crashed before turn finished', "
            "updated_at = ? "
            "WHERE status = 'streaming'",
            (now,),
        )
        return cur.rowcount or 0


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class ChatThread:
    id: int
    title: str
    created_at: str
    updated_at: str


@dataclass
class ChatThreadSummary:
    """Compact row for the sidebar list. Adds aggregates that we'd
    otherwise have to compute on the frontend (turn count, last turn
    status, last user text for preview)."""
    id: int
    title: str
    created_at: str
    updated_at: str
    turn_count: int
    last_status: str  # 'streaming' | 'done' | 'error' — of the most recent turn
    last_user_text: str


@dataclass
class ChatTurn:
    id: int
    thread_id: int
    turn_index: int
    user_text: str
    final_assistant_text: str
    trace: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    sources: list[dict[str, Any]] = field(default_factory=list)
    citation_index: list[dict[str, Any]] = field(default_factory=list)
    # Phase 9D — accumulated Anthropic usage for this turn.
    # Keys: input_tokens, output_tokens, cost_usd. Empty dict means
    # 'not tracked' (legacy turns from before the migration).
    usage: dict[str, Any] = field(default_factory=dict)
    status: str = "streaming"
    error_message: str | None = None
    created_at: str = ""
    updated_at: str = ""


@dataclass
class ChatThreadDetail:
    """A thread together with all its turns in order. What the API
    returns when the operator opens a thread in the UI."""
    thread: ChatThread
    turns: list[ChatTurn] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Row → dataclass conversion
# ---------------------------------------------------------------------------


def _row_to_thread(row: sqlite3.Row) -> ChatThread:
    return ChatThread(
        id=row["id"],
        title=row["title"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _row_to_turn(row: sqlite3.Row) -> ChatTurn:
    # ``usage_json`` is the Phase 9D field — may be missing if the row
    # was written against a pre-migration schema and the connection
    # somehow skipped init_db. Defensive default keeps reads
    # backwards-compatible.
    usage_raw: str
    try:
        usage_raw = row["usage_json"] or "{}"
    except (KeyError, IndexError):
        usage_raw = "{}"
    return ChatTurn(
        id=row["id"],
        thread_id=row["thread_id"],
        turn_index=row["turn_index"],
        user_text=row["user_text"],
        final_assistant_text=row["final_assistant_text"],
        trace=json.loads(row["trace_json"] or "[]"),
        events=json.loads(row["events_json"] or "[]"),
        sources=json.loads(row["sources_json"] or "[]"),
        citation_index=json.loads(row["citation_index_json"] or "[]"),
        usage=json.loads(usage_raw),
        status=row["status"],
        error_message=row["error_message"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ---------------------------------------------------------------------------
# Thread accessors
# ---------------------------------------------------------------------------


_TITLE_MAX_LEN = 80


def _derive_title(user_text: str) -> str:
    """Single-line preview from the first user message. Strips newlines
    so the sidebar renders cleanly; truncates with an ellipsis. Empty
    falls back to a placeholder so the row isn't visually blank."""
    cleaned = (user_text or "").strip().replace("\n", " ").replace("\r", " ")
    if not cleaned:
        return "(empty)"
    if len(cleaned) <= _TITLE_MAX_LEN:
        return cleaned
    return cleaned[: _TITLE_MAX_LEN - 1].rstrip() + "…"


def create_thread(
    *,
    title: str | None = None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatThread:
    """Create an empty thread. ``title`` is optional — if omitted, the
    first ``create_pending_turn`` call auto-derives one from the user
    message and rewrites it via ``update_thread_title``."""
    init_db(db_path)
    now = _now()
    final_title = title if (title and title.strip()) else "(untitled)"
    with _connect(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO chat_threads (title, created_at, updated_at) "
            "VALUES (?, ?, ?)",
            (final_title, now, now),
        )
        new_id = int(cur.lastrowid or 0)
        row = conn.execute(
            "SELECT * FROM chat_threads WHERE id = ?", (new_id,)
        ).fetchone()
    return _row_to_thread(row)


def get_thread(
    thread_id: int,
    db_path: Path = config.FEEDBACK_DB_PATH,
    *,
    include_deleted: bool = False,
) -> ChatThread | None:
    """By default ``deleted_at IS NOT NULL`` threads are invisible —
    soft-delete pattern. Pass ``include_deleted=True`` from admin
    paths that need to see them (e.g. the permanent purge sweep)."""
    init_db(db_path)
    with _connect(db_path) as conn:
        if include_deleted:
            row = conn.execute(
                "SELECT * FROM chat_threads WHERE id = ?", (thread_id,)
            ).fetchone()
        else:
            row = conn.execute(
                "SELECT * FROM chat_threads "
                "WHERE id = ? AND deleted_at IS NULL",
                (thread_id,),
            ).fetchone()
    return _row_to_thread(row) if row else None


def get_thread_detail(
    thread_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> ChatThreadDetail | None:
    """Thread + all its turns in order. Returns None if the thread
    doesn't exist; an empty thread (no turns yet) returns the wrapper
    with ``turns=[]`` so callers don't special-case."""
    thread = get_thread(thread_id, db_path)
    if thread is None:
        return None
    turns = list_turns_for_thread(thread_id, db_path)
    return ChatThreadDetail(thread=thread, turns=turns)


def list_threads(
    *,
    limit: int = 200,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> list[ChatThreadSummary]:
    """Newest threads first. Joins turn aggregates so the sidebar can
    render counts + last-message preview in one round-trip."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            """
            SELECT
                t.id           AS id,
                t.title        AS title,
                t.created_at   AS created_at,
                t.updated_at   AS updated_at,
                (SELECT COUNT(*) FROM chat_turns x WHERE x.thread_id = t.id)
                    AS turn_count,
                COALESCE(
                    (SELECT status FROM chat_turns x
                     WHERE x.thread_id = t.id
                     ORDER BY x.turn_index DESC LIMIT 1),
                    'done'
                ) AS last_status,
                COALESCE(
                    (SELECT user_text FROM chat_turns x
                     WHERE x.thread_id = t.id
                     ORDER BY x.turn_index DESC LIMIT 1),
                    ''
                ) AS last_user_text
            FROM chat_threads t
            WHERE t.deleted_at IS NULL
            ORDER BY t.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        ChatThreadSummary(
            id=r["id"],
            title=r["title"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            turn_count=r["turn_count"],
            last_status=r["last_status"],
            last_user_text=r["last_user_text"],
        )
        for r in rows
    ]


def delete_thread(
    thread_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> bool:
    """Soft-delete (Phase 13.7) — sets ``deleted_at`` to now. The row
    stays for audit / restore until the retention purge sweeps it.
    Subsequent list/get calls hide it. Returns True if a row was
    flipped, False if the thread didn't exist or was already deleted."""
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute(
            "UPDATE chat_threads SET deleted_at = ?, updated_at = ? "
            "WHERE id = ? AND deleted_at IS NULL",
            (_now(), _now(), thread_id),
        )
    return cur.rowcount > 0


def hard_delete_thread(
    thread_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> bool:
    """Permanent removal — used by the retention purge and by admin
    tooling. FK cascade removes child chat_turns."""
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute(
            "DELETE FROM chat_threads WHERE id = ?", (thread_id,)
        )
    return cur.rowcount > 0


def restore_thread(
    thread_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> bool:
    """Undo a soft-delete. The thread reappears in list/get results."""
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute(
            "UPDATE chat_threads SET deleted_at = NULL, updated_at = ? "
            "WHERE id = ? AND deleted_at IS NOT NULL",
            (_now(), thread_id),
        )
    return cur.rowcount > 0


def update_thread_title(
    thread_id: int,
    title: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> None:
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE chat_threads SET title = ?, updated_at = ? WHERE id = ?",
            (title, now, thread_id),
        )


def _touch_thread(conn: sqlite3.Connection, thread_id: int) -> None:
    """Bump ``updated_at`` so the sidebar surfaces this thread first.
    Called whenever a turn is created or updated. The caller already
    holds the connection (avoid re-locking SQLite)."""
    conn.execute(
        "UPDATE chat_threads SET updated_at = ? WHERE id = ?",
        (_now(), thread_id),
    )


# ---------------------------------------------------------------------------
# Turn accessors
# ---------------------------------------------------------------------------


def next_turn_index(
    thread_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> int:
    """Lowest unused turn_index for the thread. Helper for create_pending_turn
    — exposed so callers can also use it for client-side ordering."""
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(turn_index), -1) + 1 AS next "
            "FROM chat_turns WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()
    return int(row["next"]) if row else 0


def create_pending_turn(
    *,
    thread_id: int,
    user_text: str,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatTurn:
    """Insert a streaming turn for the given thread. Auto-assigns the
    next turn_index. If this is turn 0 and the thread title is
    ``(untitled)``, rewrite the title from the user_text so the sidebar
    shows a meaningful preview immediately."""
    if not user_text.strip():
        raise ValueError("user_text is required")
    init_db(db_path)
    now = _now()
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT COALESCE(MAX(turn_index), -1) + 1 AS next "
            "FROM chat_turns WHERE thread_id = ?",
            (thread_id,),
        ).fetchone()
        idx = int(row["next"]) if row else 0
        cur = conn.execute(
            "INSERT INTO chat_turns "
            "(thread_id, turn_index, user_text, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (thread_id, idx, user_text, now, now),
        )
        turn_id = int(cur.lastrowid or 0)
        # On turn 0, replace the placeholder title with a preview.
        if idx == 0:
            existing = conn.execute(
                "SELECT title FROM chat_threads WHERE id = ?", (thread_id,)
            ).fetchone()
            if existing and existing["title"] in ("(untitled)", "(empty)"):
                conn.execute(
                    "UPDATE chat_threads SET title = ?, updated_at = ? "
                    "WHERE id = ?",
                    (_derive_title(user_text), now, thread_id),
                )
            else:
                _touch_thread(conn, thread_id)
        else:
            _touch_thread(conn, thread_id)
        row = conn.execute(
            "SELECT * FROM chat_turns WHERE id = ?", (turn_id,)
        ).fetchone()
    return _row_to_turn(row)


def get_turn(
    turn_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> ChatTurn | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM chat_turns WHERE id = ?", (turn_id,)
        ).fetchone()
    return _row_to_turn(row) if row else None


def list_turns_for_thread(
    thread_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> list[ChatTurn]:
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM chat_turns WHERE thread_id = ? "
            "ORDER BY turn_index ASC",
            (thread_id,),
        ).fetchall()
    return [_row_to_turn(r) for r in rows]


def update_turn(
    turn_id: int,
    *,
    final_assistant_text: str | None = None,
    trace: list[dict[str, Any]] | None = None,
    events: list[dict[str, Any]] | None = None,
    sources: list[dict[str, Any]] | None = None,
    citation_index: list[dict[str, Any]] | None = None,
    usage: dict[str, Any] | None = None,
    status: str | None = None,
    error_message: str | None = None,
    db_path: Path = config.FEEDBACK_DB_PATH,
) -> ChatTurn | None:
    """Patch fields on a turn. Any subset may be omitted. Also bumps
    the parent thread's ``updated_at`` so live-streaming turns move
    the thread to the top of the sidebar in real time."""
    if status is not None and status not in ("streaming", "done", "error"):
        raise ValueError(f"invalid status: {status!r}")
    init_db(db_path)
    sets: list[str] = []
    params: list[Any] = []
    if final_assistant_text is not None:
        sets.append("final_assistant_text = ?")
        params.append(final_assistant_text)
    if trace is not None:
        sets.append("trace_json = ?")
        params.append(json.dumps(trace))
    if events is not None:
        sets.append("events_json = ?")
        params.append(json.dumps(events))
    if sources is not None:
        sets.append("sources_json = ?")
        params.append(json.dumps(sources))
    if citation_index is not None:
        sets.append("citation_index_json = ?")
        params.append(json.dumps(citation_index))
    if usage is not None:
        sets.append("usage_json = ?")
        params.append(json.dumps(usage))
    if status is not None:
        sets.append("status = ?")
        params.append(status)
    if error_message is not None:
        sets.append("error_message = ?")
        params.append(error_message)
    if not sets:
        return get_turn(turn_id, db_path)
    sets.append("updated_at = ?")
    params.append(_now())
    params.append(turn_id)
    with _connect(db_path) as conn:
        conn.execute(
            f"UPDATE chat_turns SET {', '.join(sets)} WHERE id = ?",
            tuple(params),
        )
        row = conn.execute(
            "SELECT * FROM chat_turns WHERE id = ?", (turn_id,)
        ).fetchone()
        if row is not None:
            _touch_thread(conn, row["thread_id"])
    return _row_to_turn(row) if row else None


def delete_turn(
    turn_id: int, db_path: Path = config.FEEDBACK_DB_PATH
) -> bool:
    """Delete one turn. Other turns in the thread keep their indexes —
    we never renumber, so trace_json references stay stable across
    deletions. Mostly for v2 edit-history features; v1 doesn't expose
    this in the UI."""
    init_db(db_path)
    with _connect(db_path) as conn:
        cur = conn.execute("DELETE FROM chat_turns WHERE id = ?", (turn_id,))
    return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Migration — legacy chat_sessions → single-turn threads
# ---------------------------------------------------------------------------


def _migrate_sessions_to_threads(conn: sqlite3.Connection) -> None:
    """One-time backfill of existing ``chat_sessions`` rows into the
    threads/turns model. Each legacy session becomes a single-turn
    thread. Idempotent: only runs when chat_threads is empty AND
    chat_sessions has rows — re-running init_db on an already-migrated
    DB is a no-op.

    The reconstructed trace contains only the user question and the
    final assistant text — we don't have the original tool_use blocks
    persisted for legacy sessions. Operators continuing a migrated
    thread will see the agent reference the final text but not the
    individual skill calls that produced it; that's an acceptable
    trade-off for not losing history entirely.
    """
    # Check whether legacy table even exists. If chat_sessions hasn't
    # been initialised (fresh install), there's nothing to migrate.
    try:
        sessions_table = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='chat_sessions'"
        ).fetchone()
    except sqlite3.Error:
        return
    if sessions_table is None:
        return

    threads_count_row = conn.execute(
        "SELECT COUNT(*) AS n FROM chat_threads"
    ).fetchone()
    if threads_count_row and threads_count_row["n"] > 0:
        return  # already migrated (or threads exist from new code paths)

    sessions_count_row = conn.execute(
        "SELECT COUNT(*) AS n FROM chat_sessions"
    ).fetchone()
    if not sessions_count_row or sessions_count_row["n"] == 0:
        return  # nothing to migrate

    rows = conn.execute(
        "SELECT * FROM chat_sessions ORDER BY id ASC"
    ).fetchall()
    for row in rows:
        question = row["question"] or ""
        answer = row["answer"] or ""
        ts = row["timestamp"]
        title = _derive_title(question)
        cur = conn.execute(
            "INSERT INTO chat_threads (title, created_at, updated_at) "
            "VALUES (?, ?, ?)",
            (title, ts, ts),
        )
        thread_id = int(cur.lastrowid or 0)
        # Minimal trace — one user message and the final assistant text
        # as a single text block. Sufficient for the next turn to
        # reference but loses tool_use / tool_result granularity.
        trace: list[dict[str, Any]] = []
        if question:
            trace.append({"role": "user", "content": question})
        if answer:
            trace.append(
                {"role": "assistant", "content": [{"type": "text", "text": answer}]}
            )
        # Status migration: legacy 'streaming' rows that never finished
        # get marked 'error' so the operator can re-run; otherwise
        # carry status forward.
        legacy_status_keys = row.keys()
        legacy_status = (
            row["status"] if "status" in legacy_status_keys else "done"
        )
        status_for_turn = (
            "error" if legacy_status == "streaming" else legacy_status
        )
        legacy_error = (
            row["error_message"] if "error_message" in legacy_status_keys else None
        )
        events_json = (
            row["events_json"] if "events_json" in legacy_status_keys else "[]"
        )
        hits_json = row["hits_json"] if "hits_json" in legacy_status_keys else "[]"
        citation_index_json = (
            row["citation_index_json"]
            if "citation_index_json" in legacy_status_keys
            else "[]"
        )
        conn.execute(
            "INSERT INTO chat_turns "
            "(thread_id, turn_index, user_text, final_assistant_text, "
            " trace_json, events_json, sources_json, citation_index_json, "
            " status, error_message, created_at, updated_at) "
            "VALUES (?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                thread_id,
                question,
                answer,
                json.dumps(trace),
                events_json or "[]",
                hits_json or "[]",
                citation_index_json or "[]",
                status_for_turn,
                legacy_error,
                ts,
                ts,
            ),
        )
