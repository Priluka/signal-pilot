"""SQLite online backup — Phase 13.5.

Uses SQLite's native ``conn.backup()`` API, which works on a live
database (no need to stop the backend). Produces a dated, single-file
snapshot under ``BACKUP_DIR`` (default: ``backups/`` in repo root).

Designed for a daily cron job. Optional ``--keep`` argument prunes
backups older than N days so disk doesn't fill silently.

Usage:

    .venv/bin/python scripts/backup_db.py
    .venv/bin/python scripts/backup_db.py --dest /var/backups/signal --keep 14

Restore is a plain file copy:

    cp backups/feedback-2026-06-02T12-30-00.db data/feedback.db

The backup file is portable across machines/SQLite versions because
``conn.backup()`` emits a self-contained database, not a delta.
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import config  # noqa: E402

_DEFAULT_BACKUP_DIR = _ROOT / "backups"


def backup_to(dest: Path) -> Path:
    """Stream the live DB to ``dest`` via SQLite's online backup API.
    Returns the path written. Creates parent dirs as needed."""
    src = config.FEEDBACK_DB_PATH
    if not src.exists():
        raise FileNotFoundError(f"Source DB not found: {src}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    src_conn = sqlite3.connect(src)
    try:
        dst_conn = sqlite3.connect(dest)
        try:
            # pages=-1 copies in one go; for big DBs we could chunk
            # but at our scale this finishes in milliseconds.
            src_conn.backup(dst_conn, pages=-1, progress=None)
        finally:
            dst_conn.close()
    finally:
        src_conn.close()
    return dest


def prune_older_than(dir_path: Path, keep_days: int) -> int:
    """Delete backup files older than ``keep_days``. Returns the count
    removed. We match the file pattern we wrote (``feedback-*.db``)
    so the script doesn't sweep up unrelated files."""
    if keep_days <= 0:
        return 0
    cutoff_ts = (datetime.now(timezone.utc) - timedelta(days=keep_days)).timestamp()
    removed = 0
    for p in dir_path.glob("feedback-*.db"):
        try:
            if p.stat().st_mtime < cutoff_ts:
                p.unlink()
                removed += 1
        except FileNotFoundError:
            pass
    return removed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dest",
        default=str(_DEFAULT_BACKUP_DIR),
        help="Directory to write the snapshot into",
    )
    parser.add_argument(
        "--keep",
        type=int,
        default=14,
        help="Prune backups older than N days (0 disables)",
    )
    args = parser.parse_args()

    dest_dir = Path(args.dest)
    stamp = (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace(":", "-")
    )
    dest_file = dest_dir / f"feedback-{stamp}.db"

    written = backup_to(dest_file)
    size = os.path.getsize(written)
    print(f"backup written: {written} ({size} bytes)")

    if args.keep > 0:
        removed = prune_older_than(dest_dir, args.keep)
        if removed:
            print(f"pruned {removed} backups older than {args.keep} days")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
