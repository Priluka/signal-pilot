"""Backend API tests for signal-pilot.

Strategy:
    * Read-only endpoints (playbooks, categories, graph, health) run against
      the real ``data/playbooks/`` directory — there's no benefit to faking
      122 mini-fixtures when the count itself is part of what's tested.
    * Endpoints that hit Claude (classify, draft, chat) inject a fake
      Anthropic client via ``fake_anthropic`` — zero real tokens spent.
    * Endpoints that hit Jira mock ``httpx.Client`` so no network request
      is made.
    * Writes (feedback, suggestions, agent sessions) go to a per-test tmp
      SQLite via the ``fresh_db`` fixture, so tests don't pollute the real
      DB and run order doesn't matter.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Playbooks — read-only, no mocks
# ---------------------------------------------------------------------------

def test_get_playbooks_returns_122(client):
    res = client.get("/playbooks")
    assert res.status_code == 200
    assert len(res.json()) == 122


def test_get_playbooks_filter_by_country_hr(client):
    res = client.get("/playbooks?country=hr")
    assert res.status_code == 200
    body = res.json()
    assert len(body) > 0
    # Every returned playbook must list 'hr' in country_focus (or 'other',
    # which is the corpus's catch-all).
    for pb in body:
        focus = set(pb["country_focus"])
        assert "hr" in focus or "other" in focus, (
            f"{pb['id']} returned for ?country=hr but country_focus={focus}"
        )


def test_get_playbooks_filter_by_ticket_class_end_user(client):
    res = client.get("/playbooks?ticket_class=end_user")
    assert res.status_code == 200
    body = res.json()
    assert len(body) > 0
    assert all(pb["ticket_class"] == "end_user" for pb in body)


def test_get_playbook_by_id_exists(client):
    # Pick the first playbook from the unfiltered list — guaranteed to exist
    # and has a stable shape.
    listing = client.get("/playbooks").json()
    pb_id = listing[0]["id"]
    res = client.get(f"/playbooks/{pb_id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["id"] == pb_id
    assert detail["title"]
    # Detail view should expose more fields than the summary.
    assert "resolution_steps" in detail
    assert "evidence_tickets" in detail


def test_get_playbook_by_id_not_found_404(client):
    res = client.get("/playbooks/this-id-does-not-exist-anywhere")
    assert res.status_code == 404


def test_get_categories_has_3_ticket_classes(client):
    res = client.get("/categories")
    assert res.status_code == 200
    body = res.json()
    names = {c["name"] for c in body["ticket_classes"]}
    assert names == {"end_user", "b2b_partner", "internal_partner"}
    assert body["total"] == 122


def test_get_playbook_graph_nodes_122(client):
    res = client.get("/playbooks/graph")
    assert res.status_code == 200
    body = res.json()
    assert len(body["nodes"]) == 122
    # Edges should be a list (may be empty for the rarely-linked corner of
    # the graph, but the field must exist).
    assert isinstance(body["edges"], list)


# ---------------------------------------------------------------------------
# Agent pipeline — Anthropic mocked
# ---------------------------------------------------------------------------

def test_classify_support_request(client, fake_anthropic):
    fake_anthropic.text_to_return = json.dumps(
        {"label": "support_request", "confidence": 0.92, "reason": "user asks for help"}
    )
    res = client.post(
        "/agent/classify",
        json={
            "summary": "Cannot pay parking",
            "description": "App says payment failed.",
            "labels": ["app"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["label"] == "support_request"
    assert body["confidence"] == 0.92
    assert "help" in body["reason"]


def test_classify_internal_log(client, fake_anthropic):
    fake_anthropic.text_to_return = json.dumps(
        {"label": "internal_log", "confidence": 0.88, "reason": "time tracking note"}
    )
    res = client.post(
        "/agent/classify",
        json={
            "summary": "Daily worklog",
            "description": "Spent 2h on documentation.",
            "labels": [],
        },
    )
    assert res.status_code == 200
    assert res.json()["label"] == "internal_log"


def test_retrieve_returns_top3(client):
    res = client.post(
        "/agent/retrieve",
        json={
            "summary": "Parking session still open after exit",
            "description": "I left the garage but the app shows active session.",
            "labels": [],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert len(body["hits"]) == 3  # default top_k
    # Hits are ranked — score should be monotonically non-increasing.
    scores = [h["score"] for h in body["hits"]]
    assert scores == sorted(scores, reverse=True)


def test_retrieve_with_country_filter(client):
    # Croatian-language ticket with HR labels should bias toward HR playbooks.
    res = client.post(
        "/agent/retrieve",
        json={
            "summary": "Ne mogu platiti parking u Splitu",
            "description": "Aplikacija prijavljuje grešku kod plaćanja.",
            "labels": ["croatia"],
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["detected_country"] == "hr"
    # Top hit must include 'hr' or 'other' in country_focus — never an
    # Italy-only or Austria-only playbook.
    for hit in body["hits"]:
        focus = set(hit["country_focus"])
        assert "hr" in focus or "other" in focus


def test_draft_generates_response(client, fake_anthropic):
    # First pick a real playbook ID so the drafter has a body to work against.
    pb_id = client.get("/playbooks").json()[0]["id"]
    fake_anthropic.text_to_return = json.dumps(
        {
            "draft": "Hello, thank you for reaching out — we are looking into your session.",
            "recommended_action": "send_with_review",
            "rationale": "user-facing reply with manual review",
        }
    )
    res = client.post(
        "/agent/draft",
        json={
            "ticket_summary": "Parking session still open",
            "ticket_description": "Left the garage at 18:30, app still active.",
            "playbook_id": pb_id,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["draft"].startswith("Hello")
    assert body["recommended_action"] in {
        "send_draft",
        "send_with_review",
        "escalate_to_human",
        "auto_close",
    }


def test_draft_includes_safety_constraints(client, fake_anthropic):
    """Drafter must surface its recommended action so the operator UI can
    decide whether to auto-send, route to review, or escalate."""
    pb_id = client.get("/playbooks").json()[0]["id"]
    fake_anthropic.text_to_return = json.dumps(
        {
            "draft": "I need to escalate this to our specialist team.",
            "recommended_action": "escalate_to_human",
            "rationale": "issue requires manual verification of payment records",
        }
    )
    res = client.post(
        "/agent/draft",
        json={
            "ticket_summary": "Double charged",
            "ticket_description": "I see two charges for the same parking session.",
            "playbook_id": pb_id,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["recommended_action"] == "escalate_to_human"
    assert body["rationale"]


# ---------------------------------------------------------------------------
# Feedback — isolated DB
# ---------------------------------------------------------------------------

def test_submit_feedback_approve(client, fresh_db):
    res = client.post(
        "/feedback",
        json={
            "ticket_id": "TEST-1",
            "playbook_id": "pb-x",
            "draft_text": "Hello, here's the answer.",
            "final_text": None,
            "status": "approved",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "approved"
    assert body["ticket_id"] == "TEST-1"
    assert body["id"] >= 1


def test_submit_feedback_reject(client, fresh_db):
    res = client.post(
        "/feedback",
        json={
            "ticket_id": "TEST-2",
            "playbook_id": "pb-x",
            "draft_text": "Wrong answer.",
            "final_text": None,
            "status": "rejected",
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "rejected"


def test_feedback_stats_counts(client, fresh_db):
    for i, status in enumerate(["approved", "approved", "rejected"]):
        client.post(
            "/feedback",
            json={
                "ticket_id": f"TEST-{i}",
                "playbook_id": "pb-x",
                "draft_text": "draft",
                "final_text": None,
                "status": status,
            },
        )
    res = client.get("/feedback/stats")
    assert res.status_code == 200
    body = res.json()
    assert body["approved"] == 2
    assert body["rejected"] == 1
    assert body["total"] == 3


# ---------------------------------------------------------------------------
# Suggestions — isolated DB, subprocess mocked, file restored at teardown
# ---------------------------------------------------------------------------

def test_create_suggestion(client, fresh_db):
    pb_id = client.get("/playbooks").json()[0]["id"]
    res = client.post(
        "/suggestions",
        json={
            "playbook_id": pb_id,
            "section": "resolution_flow",
            "step_number": 1,
            "old_text": "Acknowledge the issue.",
            "new_text": "Apologize and acknowledge the issue.",
            "author": "tester",
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "pending"
    assert body["playbook_id"] == pb_id
    assert body["author"] == "tester"


def _find_playbook_with_unique_step(client) -> tuple[str, Path, str]:
    """Walk a few playbooks until we find one whose first resolution step is
    a non-empty string that appears exactly once in its file body. Returns
    the playbook id, the on-disk path, and the unique text."""
    listing = client.get("/playbooks").json()
    for pb_summary in listing[:20]:
        detail = client.get(f"/playbooks/{pb_summary['id']}").json()
        for step in detail.get("resolution_steps") or []:
            text = (step or "").strip()
            if len(text) < 30:
                continue
            # Resolve disk path via app state (set up by lifespan).
            import config
            # The id-to-path mapping isn't exposed in the API; walk the dir.
            for path in Path(config.PLAYBOOKS_DIR).rglob("*.md"):
                content = path.read_text(encoding="utf-8")
                if f"id: {pb_summary['id']}" in content and content.count(text) == 1:
                    return pb_summary["id"], path, text
    raise pytest.skip.Exception("Could not find a suitable playbook for the accept test")


def test_accept_suggestion_rewrites_file(client, fresh_db, monkeypatch):
    pb_id, path, old_text = _find_playbook_with_unique_step(client)
    original_content = path.read_text(encoding="utf-8")
    new_text = old_text + " (edited by tester)"

    # Mock subprocess.run so we don't make a real git commit.
    mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=b""))
    monkeypatch.setattr("core.suggestions.subprocess.run", mock_run)

    try:
        post = client.post(
            "/suggestions",
            json={
                "playbook_id": pb_id,
                "section": "resolution_flow",
                "step_number": 1,
                "old_text": old_text,
                "new_text": new_text,
                "author": "tester",
            },
        )
        assert post.status_code == 200
        sug_id = post.json()["id"]

        accept = client.put(f"/suggestions/{sug_id}/accept")
        assert accept.status_code == 200
        assert accept.json()["status"] == "accepted"

        # File must contain the new text and be byte-different from the
        # original. (We can't assert ``old_text not in updated`` because the
        # new text is built by appending to the old, so the substring
        # survives — checking for an actual modification is enough.)
        updated = path.read_text(encoding="utf-8")
        assert new_text in updated
        assert updated != original_content

        # git add + git commit must have been called.
        assert mock_run.call_count == 2
        args_list = [c.args[0] for c in mock_run.call_args_list]
        assert any("add" in args for args in args_list)
        assert any("commit" in args for args in args_list)
    finally:
        # Always restore the original file content so the dev's data dir
        # isn't permanently modified by running tests.
        path.write_text(original_content, encoding="utf-8")


def test_suggestion_events_appear_in_activity_log(client, fresh_db, monkeypatch):
    """Creating, accepting and rejecting suggestions all emit events in the
    Activity Log feed alongside agent events."""
    pb_id, path, old_text = _find_playbook_with_unique_step(client)
    original_content = path.read_text(encoding="utf-8")
    new_text = old_text + " (edited for log test)"

    mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=b""))
    monkeypatch.setattr("core.suggestions.subprocess.run", mock_run)

    try:
        # 1. Create — should emit suggestion_created.
        created = client.post(
            "/suggestions",
            json={
                "playbook_id": pb_id,
                "section": "resolution_flow",
                "step_number": 3,
                "old_text": old_text,
                "new_text": new_text,
                "author": "tester",
            },
        ).json()
        sug1_id = created["id"]

        # 2. Accept — should emit suggestion_accepted.
        client.put(f"/suggestions/{sug1_id}/accept")

        # 3. Create another + reject — should emit suggestion_rejected.
        sug2 = client.post(
            "/suggestions",
            json={
                "playbook_id": pb_id,
                "section": "risks",
                "step_number": None,
                "old_text": "throwaway",
                "new_text": "throwaway edited",
                "author": "tester",
            },
        ).json()
        client.put(f"/suggestions/{sug2['id']}/reject")

        activity = client.get("/agent/activity").json()
        types = [e["event_type"] for e in activity]
        assert "suggestion_created" in types
        assert "suggestion_accepted" in types
        assert "suggestion_rejected" in types

        # Every suggestion event is grouped under the playbook id.
        for ev in activity:
            if ev["event_type"].startswith("suggestion_"):
                assert ev["ticket_id"] == pb_id

        # Accepted event's detail line should reference the suggestion id.
        accepted = [e for e in activity if e["event_type"] == "suggestion_accepted"]
        assert any(f"#{sug1_id}" in e["detail"] for e in accepted)
    finally:
        path.write_text(original_content, encoding="utf-8")


def test_add_suggestion_inserts_step(client, fresh_db, monkeypatch):
    """type=add appends a numbered step to Typical resolution flow."""
    # Pick a playbook with an existing resolution flow we can extend.
    import config
    target_path: Path | None = None
    target_id: str | None = None
    for path in Path(config.PLAYBOOKS_DIR).rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if "## Typical resolution flow" in text and "\n1. " in text:
            target_path = path
            for line in text.splitlines():
                if line.startswith("id: "):
                    target_id = line.split("id: ", 1)[1].strip()
                    break
            if target_id:
                break
    assert target_path is not None and target_id is not None
    original_content = target_path.read_text(encoding="utf-8")

    mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=b""))
    monkeypatch.setattr("core.suggestions.subprocess.run", mock_run)

    try:
        post = client.post(
            "/suggestions",
            json={
                "playbook_id": target_id,
                "section": "resolution_flow",
                "type": "add",
                "position": "end",
                "new_text": "Test step appended by suite",
                "author": "tester",
            },
        )
        assert post.status_code == 200
        body = post.json()
        assert body["type"] == "add"
        assert body["position"] == "end"

        accept = client.put(f"/suggestions/{body['id']}/accept")
        assert accept.status_code == 200, accept.json()
        assert accept.json()["status"] == "accepted"

        updated = target_path.read_text(encoding="utf-8")
        # New step should appear in the file.
        assert "Test step appended by suite" in updated
        # And it should be at the end of the numbered list, so the file
        # has grown by one numbered item.
        original_steps = sum(
            1 for line in original_content.splitlines()
            if re.match(r"^\d+\. ", line)
        )
        new_steps = sum(
            1 for line in updated.splitlines()
            if re.match(r"^\d+\. ", line)
        )
        assert new_steps == original_steps + 1
    finally:
        target_path.write_text(original_content, encoding="utf-8")


def test_add_suggestion_inserts_bullet(client, fresh_db, monkeypatch):
    """type=add appends a bullet to When this applies."""
    import config
    target_path: Path | None = None
    target_id: str | None = None
    for path in Path(config.PLAYBOOKS_DIR).rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if "## When this applies" in text and "\n- " in text:
            target_path = path
            for line in text.splitlines():
                if line.startswith("id: "):
                    target_id = line.split("id: ", 1)[1].strip()
                    break
            if target_id:
                break
    assert target_path is not None and target_id is not None
    original_content = target_path.read_text(encoding="utf-8")

    mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=b""))
    monkeypatch.setattr("core.suggestions.subprocess.run", mock_run)

    try:
        post = client.post(
            "/suggestions",
            json={
                "playbook_id": target_id,
                "section": "when_applies",
                "type": "add",
                "position": "end",
                "new_text": "Test condition appended by suite",
                "author": "tester",
            },
        )
        assert post.status_code == 200

        accept = client.put(f"/suggestions/{post.json()['id']}/accept")
        assert accept.status_code == 200

        updated = target_path.read_text(encoding="utf-8")
        assert "- Test condition appended by suite" in updated
    finally:
        target_path.write_text(original_content, encoding="utf-8")


def test_remove_suggestion_deletes_step(client, fresh_db, monkeypatch):
    """type=remove deletes a line and renumbers subsequent steps."""
    pb_id, path, old_text = _find_playbook_with_unique_step(client)
    original_content = path.read_text(encoding="utf-8")

    mock_run = MagicMock(return_value=MagicMock(returncode=0, stderr=b""))
    monkeypatch.setattr("core.suggestions.subprocess.run", mock_run)

    try:
        post = client.post(
            "/suggestions",
            json={
                "playbook_id": pb_id,
                "section": "resolution_flow",
                "type": "remove",
                "step_number": 1,
                "old_text": old_text,
                "author": "tester",
            },
        )
        assert post.status_code == 200, post.json()
        body = post.json()
        assert body["type"] == "remove"

        accept = client.put(f"/suggestions/{body['id']}/accept")
        assert accept.status_code == 200, accept.json()

        updated = path.read_text(encoding="utf-8")
        # The bare step text should no longer appear in the file.
        assert old_text not in updated
        # And the file must have shrunk (the line is gone).
        assert len(updated) < len(original_content)
    finally:
        path.write_text(original_content, encoding="utf-8")


def test_reject_suggestion_no_file_change(client, fresh_db, monkeypatch):
    # Use a real playbook ID so the suggestion can be looked up.
    pb_id = client.get("/playbooks").json()[0]["id"]
    # Find the on-disk file so we can verify it's untouched.
    import config
    pb_path = None
    for path in Path(config.PLAYBOOKS_DIR).rglob("*.md"):
        if f"id: {pb_id}" in path.read_text(encoding="utf-8"):
            pb_path = path
            break
    assert pb_path is not None

    original_content = pb_path.read_text(encoding="utf-8")

    # Guard: subprocess.run must NOT be called on a reject.
    mock_run = MagicMock(side_effect=AssertionError("reject must not invoke git"))
    monkeypatch.setattr("core.suggestions.subprocess.run", mock_run)

    post = client.post(
        "/suggestions",
        json={
            "playbook_id": pb_id,
            "section": "resolution_flow",
            "step_number": 1,
            "old_text": "any text",
            "new_text": "any other text",
            "author": "tester",
        },
    )
    assert post.status_code == 200
    sug_id = post.json()["id"]

    reject = client.put(f"/suggestions/{sug_id}/reject")
    assert reject.status_code == 200
    assert reject.json()["status"] == "rejected"

    # File must be byte-identical to before.
    assert pb_path.read_text(encoding="utf-8") == original_content
    mock_run.assert_not_called()


# ---------------------------------------------------------------------------
# Chat — stream_answer mocked
# ---------------------------------------------------------------------------

def test_chat_answer_returns_sse_stream(client, fresh_db, monkeypatch):
    """The /chat/answer endpoint emits a sources event and at least one delta.
    We mock the generator so the test runs without hitting Claude."""

    def fake_stream(*, question, playbooks):
        yield "Hello "
        yield "from "
        yield "the stub."

    monkeypatch.setattr("backend.routers.chat.stream_answer", fake_stream)
    monkeypatch.setattr(
        "backend.routers.chat.extract_cited_ids",
        lambda text, playbooks: [],
    )

    with client.stream(
        "POST", "/chat/answer", json={"question": "what is parking?", "top_k": 3}
    ) as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        body = b"".join(resp.iter_bytes()).decode("utf-8")

    assert "event: sources" in body
    assert "event: done" in body or "event: delta" in body


# ---------------------------------------------------------------------------
# Jira — httpx mocked
# ---------------------------------------------------------------------------

def _fake_httpx_client(get_response=None, post_response=None):
    """Build a context-manager-compatible mock that mirrors httpx.Client.

    Mirrors only the bits jira_client touches: ``with httpx.Client(...) as c:
    c.get(...) / c.post(...)``.
    """
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    if get_response is not None:
        mock_client.get = MagicMock(return_value=get_response)
    if post_response is not None:
        mock_client.post = MagicMock(return_value=post_response)
    return mock_client


def _ok(payload):
    r = MagicMock()
    r.status_code = 200
    r.json = MagicMock(return_value=payload)
    r.raise_for_status = MagicMock()
    return r


def test_jira_tickets_returns_list(client, monkeypatch):
    jira_response = {
        "issues": [
            {
                "id": "10004",
                "key": "TEST-1",
                "fields": {
                    "summary": "Parking session stuck",
                    "status": {"name": "To Do", "statusCategory": {"key": "new"}},
                    "priority": {"name": "High"},
                    "labels": ["app"],
                    "reporter": {
                        "emailAddress": "user@example.com",
                        "displayName": "Test User",
                    },
                    "created": "2026-05-18T12:00:00+0200",
                    "resolutiondate": None,
                },
            }
        ]
    }
    fake = _fake_httpx_client(get_response=_ok(jira_response))
    monkeypatch.setattr("core.jira_client.httpx.Client", lambda **kwargs: fake)

    res = client.get("/jira/tickets")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 1
    assert body[0]["key"] == "TEST-1"
    assert body[0]["summary"] == "Parking session stuck"
    assert body[0]["priority"] == "High"
    assert body[0]["reporter_email"] == "user@example.com"


def test_jira_process_creates_session(client, fresh_db, fake_anthropic, monkeypatch):
    """End-to-end Jira process: fetch + classify + retrieve + draft."""
    issue_payload = {
        "id": "10005",
        "key": "TEST-2",
        "fields": {
            "summary": "Open parking session after exit",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Left garage at 18:30, app still active.",
                            }
                        ],
                    }
                ],
            },
            "status": {"name": "To Do", "statusCategory": {"key": "new"}},
            "priority": {"name": "Medium"},
            "labels": [],
            "reporter": {"emailAddress": "u@x.com", "displayName": "U"},
            "assignee": None,
            "issuetype": {"name": "Task"},
            "resolution": None,
            "resolutiondate": None,
            "created": "2026-05-18T18:00:00+0200",
            "project": {"key": "TEST"},
            "comment": {"total": 0},
        },
    }
    fake = _fake_httpx_client(get_response=_ok(issue_payload))
    monkeypatch.setattr("core.jira_client.httpx.Client", lambda **kwargs: fake)

    # Classifier returns support_request so the pipeline continues into draft.
    # Drafter is also called via this same fake (different system prompt, but
    # the stub doesn't care). The classifier needs the first call's text; the
    # drafter overrides it on its turn — so we set a single response that
    # parses as both. Workaround: use a side-effect that returns the right
    # text per call.
    classifier_text = json.dumps(
        {"label": "support_request", "confidence": 0.93, "reason": "user help request"}
    )
    drafter_text = json.dumps(
        {
            "draft": "Hello, looking into your session now.",
            "recommended_action": "send_with_review",
            "rationale": "needs operator review",
        }
    )
    responses = iter([classifier_text, drafter_text])

    def next_text(**kwargs):
        from tests.conftest import FakeMessage

        try:
            return FakeMessage(next(responses))
        except StopIteration:
            return FakeMessage(drafter_text)

    fake_anthropic.create = next_text  # type: ignore[assignment]

    res = client.post("/jira/process/TEST-2")
    assert res.status_code == 200
    body = res.json()
    assert body["ticket_id"] == "TEST-2"
    assert body["classification"]["label"] == "support_request"
    assert body["draft"]["draft"].startswith("Hello")


def test_jira_comment_posts_successfully(client, monkeypatch):
    jira_post_response = _ok(
        {
            "id": "12345",
            "created": "2026-05-18T19:00:00.000+0200",
            "author": {"displayName": "Bot"},
        }
    )
    fake = _fake_httpx_client(post_response=jira_post_response)
    monkeypatch.setattr("core.jira_client.httpx.Client", lambda **kwargs: fake)

    res = client.post(
        "/jira/comment",
        json={"issue_key": "TEST-3", "body": "Hello, this is the reply."},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == "12345"
    assert body["issue_key"] == "TEST-3"
    assert body["author"] == "Bot"

    # The body sent to Jira must be wrapped in ADF format.
    sent_payload = fake.post.call_args.kwargs["json"]
    assert sent_payload["body"]["type"] == "doc"
    assert sent_payload["body"]["version"] == 1


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_returns_122_playbooks(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["playbooks_loaded"] == 122
