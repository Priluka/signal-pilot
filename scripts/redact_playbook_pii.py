"""Strip PII from all playbook .md files.

Walks ``data/playbooks/**.md``, applies the aggressive PII redactor,
and writes the cleaned file back. Catches:

  • OIB (Croatian tax id, with or without 'OIB:' label)
  • Emails
  • Plates (HR/AT/DE patterns)
  • Phone numbers (+385 / 0xx Croatian)
  • IBAN
  • ALL-CAPS Croatian person names (KATARINA PAVIČIĆ, IVAN HORVAT)
  • Datatrans transaction ids
  • SKIDATA session ids
  • Internal user ids

Usage:

    .venv/bin/python scripts/redact_playbook_pii.py            # dry-run preview
    .venv/bin/python scripts/redact_playbook_pii.py --apply    # write changes
    .venv/bin/python scripts/redact_playbook_pii.py --apply --backup

``--backup`` saves each modified file to ``<path>.bak.pii`` before
overwriting so you can diff / restore if a regex over-redacted.

Dry-run prints a per-file summary of how many bytes / patterns hit.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import config  # noqa: E402
from core.pii import redact_pii_aggressive  # noqa: E402


def _diff_summary(before: str, after: str) -> tuple[int, list[tuple[str, str]]]:
    """Return (chars_changed, list of (before_snippet, after_snippet))."""
    changed = sum(1 for a, b in zip(before, after) if a != b)
    changed += abs(len(before) - len(after))
    snippets: list[tuple[str, str]] = []
    # Find redaction markers in the after text and grab the original
    # span at the same character offset for a side-by-side preview.
    markers = (
        "[REDACTED]",
        "[REDACTED_NAME]",
        "[REDACTED_PHONE]",
    )
    cursor = 0
    while cursor < len(after) and len(snippets) < 6:
        # Scan for the next marker.
        next_idx = -1
        for m in markers:
            i = after.find(m, cursor)
            if i != -1 and (next_idx == -1 or i < next_idx):
                next_idx = i
        if next_idx == -1:
            break
        start = max(0, next_idx - 40)
        end = min(len(after), next_idx + 60)
        # Try to find the corresponding original text by relative
        # position (not perfect when lengths differ, but useful).
        b_start = max(0, start)
        b_end = min(len(before), end + (len(before) - len(after)))
        snippets.append(
            (before[b_start:b_end].strip(), after[start:end].strip())
        )
        cursor = next_idx + len(markers[0])
    return changed, snippets


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write redacted files (default is dry-run)",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Save each modified file to <path>.bak.pii before overwriting",
    )
    parser.add_argument(
        "--root",
        default=str(config.PLAYBOOKS_DIR),
        help="Playbooks directory (defaults to config.PLAYBOOKS_DIR)",
    )
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"ERROR: playbooks dir not found: {root}", file=sys.stderr)
        return 2

    files = sorted(root.rglob("*.md"))
    print(f"scanning {len(files)} .md files in {root}")
    print(f"mode: {'APPLY' if args.apply else 'DRY-RUN'}\n")

    total_changed_files = 0
    total_changed_bytes = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        cleaned = redact_pii_aggressive(original)
        if cleaned == original:
            continue
        chars_changed, snippets = _diff_summary(original, cleaned)
        total_changed_files += 1
        total_changed_bytes += chars_changed
        rel = path.relative_to(root)
        print(f"\n{rel}  ({chars_changed} chars changed)")
        for before, after in snippets[:4]:
            print(f"    - {before!r}")
            print(f"    + {after!r}")

        if args.apply:
            if args.backup:
                backup_path = path.with_suffix(path.suffix + ".bak.pii")
                shutil.copy2(path, backup_path)
            path.write_text(cleaned, encoding="utf-8")

    print(
        f"\n{'wrote' if args.apply else 'would write'} "
        f"{total_changed_files} files, "
        f"{total_changed_bytes} chars redacted"
    )
    if not args.apply and total_changed_files > 0:
        print("\nrun with --apply to write changes. add --backup for safety.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
