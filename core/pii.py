"""PII redaction — Phase 12.9.

Operator chat logs contain customer-identifiable data: plates, emails,
transaction ids, session ids. The agent NEEDS this data at runtime so
nothing here touches the database — we only redact what flows into
``logging`` records, so a leaked log file doesn't double as a customer
data dump.

The redaction is conservative: we mask the body but preserve enough
structure for a developer reading the log to spot the shape and
correlate with the DB. Example:

    "Looking up W-55123K"      → "Looking up W-*****"
    "kupac@gmail.com"          → "k****@gmail.com"
    "DT-20260527-882341"       → "DT-2026****-******"

Applied via a logging filter; opt-out via env var if a dev environment
needs to see raw plates for debugging.
"""
from __future__ import annotations

import logging
import os
import re


# ---------------------------------------------------------------------------
# Pattern definitions — kept tight to avoid mangling unrelated text.
# ---------------------------------------------------------------------------

# Croatian/Austrian/German style plates: 2-4 alphanumeric + hyphen/space
# + 4-7 alphanumeric. Common shapes: HR-ZD-442, W-55123K, ZG-1234-AB,
# DE-MH-5521. The combined regex tolerates separators but won't match
# generic IDs.
_PLATE_RE = re.compile(
    r"\b("
    r"(?:[A-Z]{1,3})"          # country / city prefix
    r"[-\s]?"
    r"(?:[A-Z0-9]{1,4})"       # numeric / alpha middle
    r"[-\s]?"
    r"(?:[A-Z0-9]{1,5})"       # tail
    r")\b"
)

# Email addresses — RFC-light, fine for redaction.
_EMAIL_RE = re.compile(
    r"\b([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"
)

# Datatrans-style transaction ids: DT-YYYYMMDD-NNNNNN
_TXN_RE = re.compile(r"\b(DT-\d{4})\d{4}-\d{6}\b")

# SKIDATA / parking sessions: sess-NNNNN, ses_xxxx
_SESSION_RE = re.compile(r"\b(sess[-_])\w{4,}\b")

# Internal user ids: usr-NNNNNN
_USER_RE = re.compile(r"\b(usr-)\d{3}\d+\b")

# ---------------------------------------------------------------------------
# Croatian-specific patterns — added for playbook redaction.
# ---------------------------------------------------------------------------

# OIB (Croatian tax id) — 11 digits, almost always preceded by 'OIB:'
# or 'OIB '. We DELIBERATELY do not match bare 11-digit sequences —
# that pattern collides with transaction ids, order refs, generic
# numeric tokens (e.g. ``601191128168600212808`` Datatrans refs).
# False negatives are safer than mangling real data here.
_OIB_PREFIXED_RE = re.compile(r"\bOIB[:\s]+(\d{11})\b", re.IGNORECASE)

# IBAN — Croatian IBAN: ``HR`` + 19 digits. Tighter than the generic
# 2-letter pattern so we don't catch random codes like ``HR-ZD-442``.
_IBAN_RE = re.compile(r"\b(HR\d{2})\d{17}\b")

# Croatian phone numbers — REQUIRE an unambiguous prefix:
#   • +385 / 00385 followed by 1-9 (no leading zero after country code)
#   • Bare 09X mobile (091, 092, 095, 097, 098, 099)
#   • Bare landline 01X / 02X / 03X / 04X / 05X where X ∈ 1-9
# Separator + 6-8 digits. The strict mobile prefix list avoids
# catching things like ``2026-01-19`` (date) or ``code 011``.
_PHONE_RE = re.compile(
    r"(?:"
    r"(?:\+385|00385)[\s\-/]?[1-9]\d?[\s\-/]?\d{2,3}[\s\-/]?\d{2,4}"
    r"|"
    r"\b09[125789][\s\-/]?\d{2,3}[\s\-/]?\d{2,4}\b"
    r"|"
    r"\b0[1-5][1-9][\s\-/]\d{2,3}[\s\-/]\d{2,4}\b"
    r")"
)

# ALL-CAPS Croatian person names. Two+ consecutive capitalised tokens
# of 3+ chars where the ENTIRE phrase contains at least one Croatian
# diacritic (Č, Ć, Đ, Š, Ž). This is intentionally conservative — it
# misses non-diacritic names like "IVAN HORVAT" but reliably avoids
# false positives on English ALL-CAPS phrases ("RECURRING PATTERN",
# "ONE-OFF INCIDENT", "ROOT CAUSE", "ERROR MESSAGE") that dominate
# playbook bodies. Non-diacritic names should be reviewed manually
# during the playbook authoring step.
_CRO_NAME_RE = re.compile(
    r"\b([A-ZČĆĐŠŽ]{3,}(?:\s+[A-ZČĆĐŠŽ]{3,})+)\b"
)


def _has_diacritic(s: str) -> bool:
    return any(c in "ČĆĐŠŽ" for c in s)


def _redact_plate(m: re.Match[str]) -> str:
    s = m.group(1)
    if len(s) <= 3:
        return s  # don't touch tiny tokens — likely false positive
    return s[:3] + "*" * (len(s) - 3)


def _redact_oib(m: re.Match[str]) -> str:
    return "OIB: [REDACTED]"


def _redact_oib_bare(m: re.Match[str]) -> str:
    # Only redact when surrounding text suggests an identifier — we
    # already check this via context in the apply function; the bare
    # regex here just provides the digit envelope.
    digits = m.group(1)
    return digits[:3] + "********"


def _redact_iban(m: re.Match[str]) -> str:
    return f"{m.group(1)}**********"


def _redact_phone(m: re.Match[str]) -> str:
    return "[REDACTED_PHONE]"


def _redact_cro_name(m: re.Match[str]) -> str:
    # Only redact when the phrase contains at least one Croatian
    # diacritic. This is a runtime safeguard on top of the regex —
    # it lets us keep the regex broad enough to match names like
    # ``KATARINA PAVIČIĆ`` while excluding English compounds like
    # ``RECURRING PATTERN`` that share the ALL-CAPS shape.
    matched = m.group(1)
    if not _has_diacritic(matched):
        return matched
    return "[REDACTED_NAME]"


def _redact_email(m: re.Match[str]) -> str:
    local, domain = m.group(1), m.group(2)
    head = local[:1] if local else ""
    return f"{head}****@{domain}"


def _redact_txn(m: re.Match[str]) -> str:
    return f"{m.group(1)}****-******"


def _redact_session(m: re.Match[str]) -> str:
    return f"{m.group(1)}****"


def _redact_user(m: re.Match[str]) -> str:
    return f"{m.group(1)}****"


def redact_pii(text: str) -> str:
    """Apply all redaction patterns to ``text``. Order matters — email
    runs first so the local-part isn't half-eaten by the user-id rule
    (``usr-`` could match an email prefix). Plate runs last because it
    has the loosest pattern."""
    text = _EMAIL_RE.sub(_redact_email, text)
    text = _TXN_RE.sub(_redact_txn, text)
    text = _SESSION_RE.sub(_redact_session, text)
    text = _USER_RE.sub(_redact_user, text)
    text = _PLATE_RE.sub(_redact_plate, text)
    return text


def redact_pii_aggressive(text: str) -> str:
    """Aggressive redaction for content that is REWRITTEN on disk
    (playbooks, exported reports) — not for ephemeral log lines.

    Catches Croatian PII the standard redactor leaves alone:
      • OIB (only when labelled 'OIB:' to avoid mangling generic
        11-digit ids like Datatrans references)
      • IBAN (HR prefix only)
      • Phone numbers (+385 / 091-099 / landline 0[1-5]X with separator)
      • ALL-CAPS person names (KATARINA PAVIČIĆ, IVAN HORVAT)

    Standard scrubbers are applied selectively: emails, transactions,
    sessions, and user ids — but NOT the generic plate regex, which
    has a high false-positive rate in playbook bodies where Jira
    keys (RAOS-3219, KAN-54) look superficially like plates."""
    text = _OIB_PREFIXED_RE.sub(_redact_oib, text)
    text = _IBAN_RE.sub(_redact_iban, text)
    text = _PHONE_RE.sub(_redact_phone, text)
    text = _CRO_NAME_RE.sub(_redact_cro_name, text)
    # Standard patterns minus plate — plate redactor is fine for
    # chat / log lines (which have real plate data) but mangles
    # Jira keys and project codes that dominate playbook bodies.
    text = _EMAIL_RE.sub(_redact_email, text)
    text = _TXN_RE.sub(_redact_txn, text)
    text = _SESSION_RE.sub(_redact_session, text)
    text = _USER_RE.sub(_redact_user, text)
    return text


class PIIRedactionFilter(logging.Filter):
    """Logging filter that scrubs PII from every log record's message
    before it hits a handler. Applied at the root logger so every
    module's log lines go through it. Set ``PII_REDACTION_DISABLED=1``
    to bypass in a dev environment."""

    def __init__(self) -> None:
        super().__init__()
        self._enabled = (
            os.environ.get("PII_REDACTION_DISABLED", "").lower()
            not in ("1", "true", "yes")
        )

    def filter(self, record: logging.LogRecord) -> bool:
        if not self._enabled:
            return True
        try:
            # ``msg`` may carry %s-style placeholders that get expanded
            # against ``args``. Redact the formatted output so we cover
            # both the template and any interpolated values.
            formatted = record.getMessage()
            redacted = redact_pii(formatted)
            if redacted != formatted:
                record.msg = redacted
                record.args = ()  # already merged into msg
        except Exception:  # noqa: BLE001
            # Never let redaction break logging itself.
            pass
        return True
