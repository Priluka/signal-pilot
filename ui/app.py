"""Streamlit front-end for signal-pilot.

Run with: ``streamlit run ui/app.py``.

Three tabs:
- "Znanje": browse the 122 playbooks in a category tree, preview content.
- "Chat":   ask a free-form question, retrieve top-k playbooks, cite them.
- "Agent":  pick one of the 50 sample tickets, classify → retrieve → draft,
            then approve / edit / reject — every decision is logged to
            ``feedback.sqlite3``.

Heavy work (loading the embedding model, building the index, reading the
ticket sample) is cached so re-runs are fast.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Allow `streamlit run ui/app.py` to import the sibling `core/` package.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import streamlit as st

import config
import core.feedback as feedback
from core.classifier import classify_ticket
from core.drafter import draft_reply
from core.embeddings import get_embedding_provider
from core.retrieval import (
    Playbook,
    PlaybookIndex,
    build_index,
    country_from_labels,
    detect_language,
    retrieve,
)


st.set_page_config(page_title="Signal Pilot", layout="wide")


# ---------------------------------------------------------------------------
# Cached resource loaders
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Loading embedding model + building index…")
def _load_index() -> PlaybookIndex:
    return build_index()


@st.cache_data(show_spinner=False)
def _load_tickets() -> list[dict[str, Any]]:
    path = config.TICKET_SAMPLE_FILE
    if not path.exists():
        return []
    tickets: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tickets.append(json.loads(line))
    return tickets


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ticket_text(ticket: dict[str, Any]) -> str:
    summary = ticket.get("summary", "") or ""
    description = ticket.get("description", "") or ""
    return f"{summary}\n\n{description}".strip()


def _category_tree(playbooks: list[Playbook]) -> dict[str, dict[str, list[Playbook]]]:
    """Group playbooks by ticket_class → issue_category → [playbooks]."""
    tree: dict[str, dict[str, list[Playbook]]] = {}
    for pb in playbooks:
        cls = pb.ticket_class or "uncategorized"
        cat = pb.category or pb.issue_category or "other"
        tree.setdefault(cls, {}).setdefault(cat, []).append(pb)
    for cls in tree:
        for cat in tree[cls]:
            tree[cls][cat].sort(key=lambda p: p.title.lower())
    return tree


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
def render_knowledge_tab(index: PlaybookIndex) -> None:
    st.subheader(f"Knowledge base — {len(index)} playbooks")
    tree = _category_tree(index.playbooks)

    col_tree, col_view = st.columns([1, 2])

    with col_tree:
        ticket_classes = sorted(tree.keys())
        chosen_class = st.selectbox("Ticket class", ticket_classes)
        categories = sorted(tree[chosen_class].keys())
        chosen_cat = st.selectbox("Category", categories)
        playbooks = tree[chosen_class][chosen_cat]
        labels = [pb.title for pb in playbooks]
        idx = st.radio("Playbook", range(len(playbooks)), format_func=lambda i: labels[i])

    with col_view:
        if playbooks:
            pb = playbooks[idx]
            st.markdown(f"### {pb.title}")
            st.caption(
                f"`{pb.id}` · class=`{pb.ticket_class}` · "
                f"countries={', '.join(pb.country_focus) or '—'} · "
                f"languages={', '.join(pb.languages) or '—'}"
            )
            st.markdown(pb.body)


def render_chat_tab(index: PlaybookIndex) -> None:
    st.subheader("Ask the knowledge base")
    question = st.text_area("Your question", height=120, placeholder="e.g. What do I tell a Croatian customer who got a parking fine despite paying via the app?")
    top_k = st.slider("How many playbooks to cite", 1, 5, config.TOP_K_RETRIEVAL)

    if not st.button("Search", type="primary"):
        return
    if not question.strip():
        st.warning("Type a question first.")
        return

    provider = get_embedding_provider()
    query_vector = np.asarray(provider.embed(question), dtype=np.float32)
    hits = index.search(
        query_vector,
        country=None,
        language=detect_language(question),
        ticket_class=None,
        top_k=top_k,
    )
    if not hits:
        st.info("No matches above the confidence floor.")
        return

    for hit in hits:
        with st.expander(f"#{hit.rank + 1}  ·  {hit.playbook.title}  ·  score {hit.score:.3f}"):
            st.caption(f"`{hit.playbook.id}` · {hit.playbook.category}")
            st.markdown(hit.playbook.description)
            st.divider()
            st.markdown(hit.playbook.body)


def _render_classification(ticket: dict[str, Any]) -> None:
    with st.spinner("Classifying ticket…"):
        try:
            result = classify_ticket(
                summary=ticket.get("summary", ""),
                description=ticket.get("description", ""),
                reporter_email=ticket.get("reporter_email"),
                labels=ticket.get("labels") or [],
            )
        except Exception as exc:
            st.error(f"Classifier failed: {exc}")
            return
    st.session_state["last_classification"] = result
    st.markdown(
        f"**Classification:** `{result.label}`  ·  confidence {result.confidence:.2f}\n\n"
        f"_{result.reason}_"
    )


def _render_retrieval(index: PlaybookIndex, ticket: dict[str, Any]) -> None:
    hits = retrieve(
        index,
        _ticket_text(ticket),
        labels=ticket.get("labels") or [],
        ticket_class=None,
    )
    st.session_state["last_hits"] = hits
    if not hits:
        st.info("No playbook matched.")
        return
    options = [f"#{h.rank + 1}  ·  {h.playbook.title}  ·  score {h.score:.3f}" for h in hits]
    chosen = st.radio("Matched playbooks", range(len(hits)), format_func=lambda i: options[i])
    st.session_state["chosen_hit_idx"] = chosen
    with st.expander("Show selected playbook"):
        st.markdown(hits[chosen].playbook.body)


def _render_draft_and_feedback(ticket: dict[str, Any]) -> None:
    hits = st.session_state.get("last_hits", [])
    chosen_idx = st.session_state.get("chosen_hit_idx", 0)
    if not hits:
        return
    chosen_hit = hits[chosen_idx]

    if st.button("Generate draft", type="primary"):
        with st.spinner("Drafting reply…"):
            try:
                draft = draft_reply(
                    ticket_summary=ticket.get("summary", ""),
                    ticket_description=ticket.get("description", ""),
                    playbook=chosen_hit.playbook,
                )
            except Exception as exc:
                st.error(f"Drafter failed: {exc}")
                return
        st.session_state["last_draft"] = draft

    draft = st.session_state.get("last_draft")
    if not draft:
        return

    st.markdown(
        f"**Recommended action:** `{draft.recommended_action}`  ·  _{draft.rationale}_"
    )
    edited = st.text_area("Draft (edit before sending if needed)", value=draft.draft, height=260)

    col_a, col_e, col_r = st.columns(3)
    with col_a:
        if st.button("Approve", use_container_width=True):
            feedback.record_feedback(
                ticket_id=str(ticket.get("key", "?")),
                playbook_id=chosen_hit.playbook.id,
                draft_text=draft.draft,
                final_text=edited if edited != draft.draft else None,
                status="edited" if edited != draft.draft else "approved",
            )
            st.success("Feedback logged.")
    with col_e:
        if st.button("Save edit", use_container_width=True):
            feedback.record_feedback(
                ticket_id=str(ticket.get("key", "?")),
                playbook_id=chosen_hit.playbook.id,
                draft_text=draft.draft,
                final_text=edited,
                status="edited",
            )
            st.success("Edit logged.")
    with col_r:
        if st.button("Reject", use_container_width=True):
            feedback.record_feedback(
                ticket_id=str(ticket.get("key", "?")),
                playbook_id=chosen_hit.playbook.id,
                draft_text=draft.draft,
                status="rejected",
            )
            st.warning("Rejection logged.")


def render_agent_tab(index: PlaybookIndex) -> None:
    st.subheader("Agent Feed")
    tickets = _load_tickets()
    if not tickets:
        st.warning(
            f"No tickets at {config.TICKET_SAMPLE_FILE}. "
            "Drop a JSONL sample there to populate this tab."
        )
        return

    options = [f"{t.get('key', '?')}  ·  {(t.get('summary') or '').strip()[:80]}" for t in tickets]
    chosen = st.selectbox("Pick a ticket", range(len(tickets)), format_func=lambda i: options[i])
    ticket = tickets[chosen]

    # Clear per-ticket state when the selection changes.
    if st.session_state.get("agent_ticket_key") != ticket.get("key"):
        for k in ("last_classification", "last_hits", "last_draft", "chosen_hit_idx"):
            st.session_state.pop(k, None)
        st.session_state["agent_ticket_key"] = ticket.get("key")

    with st.expander("Ticket content", expanded=True):
        st.caption(
            f"`{ticket.get('key', '?')}` · status={ticket.get('status')} · "
            f"labels={ticket.get('labels') or []} · "
            f"reporter={ticket.get('reporter_email') or 'unknown'}"
        )
        st.markdown(f"**{ticket.get('summary', '')}**")
        st.write(ticket.get("description", ""))

    st.divider()
    st.markdown("### 1 · Classify")
    if st.button("Run classifier"):
        _render_classification(ticket)
    elif "last_classification" in st.session_state:
        r = st.session_state["last_classification"]
        st.markdown(
            f"**Classification:** `{r.label}`  ·  confidence {r.confidence:.2f}\n\n_{r.reason}_"
        )

    cls = st.session_state.get("last_classification")
    if cls and cls.label != "support_request":
        st.info(
            f"Auto-close path: this ticket was classified as `{cls.label}`. "
            "No retrieval or drafting needed."
        )
        return

    st.divider()
    st.markdown("### 2 · Retrieve")
    detected_lang = detect_language(_ticket_text(ticket))
    detected_country = country_from_labels(ticket.get("labels") or [])
    st.caption(f"Detected language: `{detected_lang or '—'}`  ·  country: `{detected_country or '—'}`")
    _render_retrieval(index, ticket)

    st.divider()
    st.markdown("### 3 · Draft & decide")
    _render_draft_and_feedback(ticket)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    st.title("Signal Pilot")
    st.caption("Support-ticket triage prototype — retrieval + drafter + feedback log")
    feedback.init_db()
    index = _load_index()

    tab_knowledge, tab_chat, tab_agent = st.tabs(["Znanje", "Chat", "Agent"])
    with tab_knowledge:
        render_knowledge_tab(index)
    with tab_chat:
        render_chat_tab(index)
    with tab_agent:
        render_agent_tab(index)


if __name__ == "__main__":
    main()
