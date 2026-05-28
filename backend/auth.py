"""Bearer-token auth for sensitive endpoints.

Single shared secret read from the ``OPERATOR_TOKEN`` env var. When set,
every request to a protected endpoint must include ``Authorization:
Bearer <token>``. When unset, auth is disabled (dev-mode) so local
development doesn't constantly trip 401s.

This is intentionally NOT a full OAuth/OIDC stack — that's overkill for
a single-tenant internal tool. The token rotates by changing the env
var and bouncing the process. Production rollout swaps this dependency
for whatever SSO the customer already uses.
"""
from __future__ import annotations

import os
import secrets

from fastapi import Header, HTTPException, status


def _expected_token() -> str | None:
    """Snapshot the env var on each call so tests can change it without
    a process restart. Empty string is treated as 'auth disabled'."""
    token = os.environ.get("OPERATOR_TOKEN", "").strip()
    return token or None


def require_operator(
    authorization: str | None = Header(default=None),
) -> str:
    """FastAPI dependency — returns the validated bearer token (so the
    caller can log who did what) or raises 401.

    Tokens are compared with ``secrets.compare_digest`` to keep timing
    leakage off the table; not vital for an internal tool, but cheap to
    do right.
    """
    expected = _expected_token()
    if expected is None:
        # Auth disabled (dev-mode). Return a sentinel so the audit log
        # still has SOMETHING to attribute the action to.
        return "anonymous-dev"

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    presented = authorization[len("Bearer ") :].strip()
    if not secrets.compare_digest(presented, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid operator token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return presented
