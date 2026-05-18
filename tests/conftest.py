"""Shared fixtures for backend API tests.

Three concerns are handled here, in this order, BEFORE any signal-pilot
module is imported by a test file:

1. ``sys.path`` — make the repo root importable so ``import config`` works.
2. Environment variables — set placeholder API keys and Jira creds so
   modules don't refuse to load. Actual outbound calls are mocked.
3. SQLite path redirect — point ``config.FEEDBACK_DB_PATH`` at a per-session
   tmp file so tests don't trample the real ``feedback.sqlite3``. This MUST
   happen before any ``core.*`` module is imported, because their persistence
   functions bind the path as a default argument at definition time.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest


_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Placeholders so import-time config checks pass. Outbound calls are mocked
# in every test that would trigger them.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-not-real")
os.environ.setdefault("JIRA_URL", "https://test.atlassian.net")
os.environ.setdefault("JIRA_EMAIL", "test@example.com")
os.environ.setdefault("JIRA_TOKEN", "test-token-not-real")
os.environ.setdefault("JIRA_PROJECT", "TEST")

import config  # noqa: E402

# Per-session temp DB; cleaned up by pytest's tmp_path management implicitly
# (we don't bother with explicit teardown — the OS reaps /tmp on reboot).
_TMP_ROOT = Path(tempfile.mkdtemp(prefix="signal-pilot-tests-"))
config.FEEDBACK_DB_PATH = _TMP_ROOT / "feedback.sqlite3"


# ---------------------------------------------------------------------------
# Helpers used by multiple tests
# ---------------------------------------------------------------------------

class FakeMessage:
    """Mimics anthropic.types.Message — only the bits our code touches."""

    def __init__(self, text: str) -> None:
        block = type("Block", (), {"text": text})()
        self.content = [block]


class FakeAnthropic:
    """Drop-in stub for the Anthropic SDK client.

    Returns a fixed JSON string from ``messages.create``. Per-test code sets
    ``text_to_return`` to control what comes back. Records the system+user
    prompts so tests can assert on what was sent.
    """

    def __init__(self) -> None:
        self.text_to_return = '{"label":"support_request","confidence":0.9,"reason":"stub"}'
        self.calls: list[dict] = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return FakeMessage(self.text_to_return)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """Build the FastAPI app exactly once per session and run its lifespan so
    the playbook index is ready. The embedding cache on disk makes the first
    build near-instant after an initial production run; if it's missing,
    expect the first test to take 30–60 s while ``bge-m3`` encodes 122
    playbooks."""
    from fastapi.testclient import TestClient
    from backend.main import app as fastapi_app

    # Enter the lifespan via TestClient context manager once; reuse for the
    # rest of the session.
    with TestClient(fastapi_app):
        yield fastapi_app


@pytest.fixture
def client(app):
    """Fresh TestClient per test — cheap, doesn't re-run lifespan."""
    from fastapi.testclient import TestClient

    return TestClient(app)


@pytest.fixture
def fake_anthropic(monkeypatch):
    """Patch ``anthropic.Anthropic`` to return a FakeAnthropic instance.

    Both ``core.classifier`` and ``core.drafter`` do ``from anthropic import
    Anthropic`` lazily INSIDE their functions, so the only reliable patch
    point is the source module — not the callsite's local binding.

    Tests get back the FakeAnthropic instance so they can set
    ``text_to_return`` and read ``calls``.
    """
    stub = FakeAnthropic()

    def _factory(api_key=None):
        return stub

    import anthropic

    monkeypatch.setattr(anthropic, "Anthropic", _factory)
    return stub


@pytest.fixture
def fresh_db():
    """Empty every persistence table at the start of the test.

    Default-arg path binding makes per-test DB redirection fragile (different
    functions cache the path at definition time, and some helpers don't
    accept the override). Pragmatic alternative: tests share the session-level
    tmp DB, but each test wipes the tables it cares about so its assertions
    don't depend on what ran before.
    """
    import sqlite3

    db_path = config.FEEDBACK_DB_PATH
    if not db_path.exists():
        return db_path
    with sqlite3.connect(db_path, timeout=30.0) as conn:
        for table in (
            "feedback",
            "suggestions",
            "agent_sessions",
            "chat_sessions",
        ):
            try:
                conn.execute(f"DELETE FROM {table}")
            except sqlite3.OperationalError:
                # Table not yet created — first call to the matching module
                # will lazily create it.
                pass
        conn.commit()
    return db_path
