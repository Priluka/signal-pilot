"""Streamlit front-end for signal-pilot.

Run with: ``streamlit run ui/app.py``.

Three tabs:
- "Znanje": browse the 122 playbooks, filtered from the sidebar, rendered as cards.
- "Chat":   ask a free-form question, retrieve top-k playbooks with colored
            confidence bars.
- "Agent":  pick one of the sample tickets, classify → retrieve → draft in a
            two-column layout (ticket | draft + decision).
"""
from __future__ import annotations

import html
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


st.set_page_config(
    page_title="Signal Pilot",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------------------------
# Theme — inject custom CSS once per session.
# ---------------------------------------------------------------------------
_STYLES_PATH = Path(__file__).with_name("styles.css")


def _inject_theme() -> None:
    css = _STYLES_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


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
# Rendering helpers
# ---------------------------------------------------------------------------
def _ticket_text(ticket: dict[str, Any]) -> str:
    summary = ticket.get("summary", "") or ""
    description = ticket.get("description", "") or ""
    return f"{summary}\n\n{description}".strip()


def _category_tree(playbooks: list[Playbook]) -> dict[str, dict[str, list[Playbook]]]:
    tree: dict[str, dict[str, list[Playbook]]] = {}
    for pb in playbooks:
        cls = pb.ticket_class or "uncategorized"
        cat = pb.category or pb.issue_category or "other"
        tree.setdefault(cls, {}).setdefault(cat, []).append(pb)
    for cls in tree:
        for cat in tree[cls]:
            tree[cls][cat].sort(key=lambda p: p.title.lower())
    return tree


def _confidence_tier(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.4:
        return "mid"
    return "low"


def confidence_bar(score: float) -> str:
    """HTML for a colored progress-bar style confidence indicator."""
    pct = max(0.0, min(1.0, float(score))) * 100
    tier = _confidence_tier(score)
    return (
        '<div class="sp-conf-wrap">'
        '<div class="sp-conf-track">'
        f'<div class="sp-conf-fill {tier}" style="width:{pct:.0f}%"></div>'
        '</div>'
        f'<div class="sp-conf-label">{score:.2f}</div>'
        '</div>'
    )


def _chips(labels: list[str]) -> str:
    return "".join(f'<span class="sp-chip">{html.escape(str(l))}</span>' for l in labels if l)


def _classification_pill(label: str) -> str:
    mapping = {
        "support_request": ("sp-pill-support", "support request"),
        "internal_log":    ("sp-pill-internal", "internal log"),
        "spam_or_junk":    ("sp-pill-spam", "spam / junk"),
    }
    cls, text = mapping.get(label, ("sp-pill-support", label))
    return f'<span class="sp-pill {cls}">{html.escape(text)}</span>'


def _action_pill(action: str) -> str:
    return f'<span class="sp-pill sp-pill-action">{html.escape(action.replace("_", " "))}</span>'


def render_playbook_card(pb: Playbook, *, score: float | None = None, expanded: bool = False) -> None:
    """A single playbook rendered as a card. Optionally shows a confidence bar."""
    meta_chips = [
        pb.ticket_class,
        pb.issue_category,
        *pb.country_focus,
        *pb.languages,
    ]
    header_html = (
        '<div class="sp-card">'
        f'<div class="sp-card-title">{html.escape(pb.title)}</div>'
        f'<div class="sp-card-meta"><code>{html.escape(pb.id)}</code>{_chips([c for c in meta_chips if c])}</div>'
    )
    if score is not None:
        header_html += confidence_bar(score)
    header_html += (
        f'<div class="sp-card-body">{html.escape(pb.description)}</div>'
        '</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)
    with st.expander("Show full playbook", expanded=expanded):
        st.markdown(pb.body)


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
def render_knowledge_tab(index: PlaybookIndex) -> None:
    tree = _category_tree(index.playbooks)
    ticket_classes = sorted(tree.keys())

    with st.sidebar:
        st.markdown("#### Filters")
        chosen_class = st.selectbox("Ticket class", ticket_classes, key="kn_class")
        categories = sorted(tree[chosen_class].keys())
        chosen_cat = st.selectbox("Category", ["All"] + categories, key="kn_cat")
        query = st.text_input("Search title / description", "", key="kn_search").strip().lower()

    if chosen_cat == "All":
        playbooks = [pb for cat in categories for pb in tree[chosen_class][cat]]
    else:
        playbooks = tree[chosen_class][chosen_cat]

    if query:
        playbooks = [
            pb for pb in playbooks
            if query in pb.title.lower() or query in pb.description.lower()
        ]

    st.markdown(f"### Knowledge base")
    st.caption(f"{len(playbooks)} of {len(index)} playbooks shown")

    if not playbooks:
        st.info("No playbooks match the current filter.")
        return

    for pb in playbooks:
        render_playbook_card(pb)


def render_chat_tab(index: PlaybookIndex) -> None:
    with st.sidebar:
        st.markdown("#### Search options")
        top_k = st.slider("How many playbooks to cite", 1, 5, config.TOP_K_RETRIEVAL, key="chat_topk")

    st.markdown("### Ask the knowledge base")
    question = st.text_area(
        "Your question",
        height=120,
        placeholder="e.g. What do I tell a Croatian customer who got a parking fine despite paying via the app?",
    )

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
        render_playbook_card(hit.playbook, score=hit.score)


# ---------- Agent tab (two-column layout) ----------------------------------
def _agent_sidebar(tickets: list[dict[str, Any]]) -> dict[str, Any]:
    with st.sidebar:
        st.markdown("#### Ticket")
        options = [
            f"{t.get('key', '?')}  ·  {(t.get('summary') or '').strip()[:60]}"
            for t in tickets
        ]
        chosen = st.selectbox(
            "Pick a ticket",
            range(len(tickets)),
            format_func=lambda i: options[i],
            key="agent_ticket_idx",
        )
    return tickets[chosen]


def _agent_left_column(ticket: dict[str, Any], index: PlaybookIndex) -> None:
    st.markdown("#### Ticket")
    summary = html.escape(ticket.get("summary") or "")
    description = html.escape(ticket.get("description") or "")
    meta = _chips([
        ticket.get("status") or "",
        ticket.get("priority") or "",
        *(ticket.get("labels") or []),
    ])
    reporter = html.escape(ticket.get("reporter_email") or "unknown")
    st.markdown(
        '<div class="sp-card">'
        f'<div class="sp-card-title">{summary}</div>'
        f'<div class="sp-card-meta"><code>{html.escape(ticket.get("key") or "?")}</code>{meta}'
        f'<span class="sp-chip">reporter: {reporter}</span></div>'
        f'<div class="sp-card-body">{description.replace(chr(10), "<br>")}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("#### 1 · Classify")
    if st.button("Run classifier", key="btn_classify"):
        with st.spinner("Classifying…"):
            try:
                result = classify_ticket(
                    summary=ticket.get("summary", ""),
                    description=ticket.get("description", ""),
                    reporter_email=ticket.get("reporter_email"),
                    labels=ticket.get("labels") or [],
                )
                st.session_state["last_classification"] = result
            except Exception as exc:
                st.error(f"Classifier failed: {exc}")
                return

    cls = st.session_state.get("last_classification")
    if cls:
        st.markdown(
            f'{_classification_pill(cls.label)} '
            f'<span class="sp-conf-label">conf {cls.confidence:.2f}</span>',
            unsafe_allow_html=True,
        )
        st.caption(cls.reason)
        if cls.label != "support_request":
            st.info(
                f"Auto-close path: this ticket was classified as `{cls.label}`. "
                "No retrieval or drafting needed."
            )
            return

    if not cls:
        return

    st.markdown("#### 2 · Retrieve")
    detected_lang = detect_language(_ticket_text(ticket))
    detected_country = country_from_labels(ticket.get("labels") or [])
    st.caption(
        f"Detected language: `{detected_lang or '—'}`  ·  country: `{detected_country or '—'}`"
    )

    if "last_hits" not in st.session_state or st.session_state.get("hits_for") != ticket.get("key"):
        with st.spinner("Retrieving playbooks…"):
            hits = retrieve(
                index,
                _ticket_text(ticket),
                labels=ticket.get("labels") or [],
                ticket_class=None,
            )
            st.session_state["last_hits"] = hits
            st.session_state["hits_for"] = ticket.get("key")
            st.session_state["chosen_hit_idx"] = 0

    hits = st.session_state.get("last_hits", [])
    if not hits:
        st.info("No playbook matched.")
        return

    for h in hits:
        st.markdown(
            f'<div class="sp-card">'
            f'<div class="sp-card-title">#{h.rank + 1}  ·  {html.escape(h.playbook.title)}</div>'
            f'<div class="sp-card-meta"><code>{html.escape(h.playbook.id)}</code>'
            f'{_chips([c for c in [h.playbook.ticket_class, *h.playbook.country_focus] if c])}</div>'
            f'{confidence_bar(h.score)}'
            f'<div class="sp-card-body">{html.escape(h.playbook.description)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    options = [f"#{h.rank + 1}  ·  {h.playbook.title}" for h in hits]
    st.radio(
        "Use which playbook for drafting?",
        range(len(hits)),
        format_func=lambda i: options[i],
        key="chosen_hit_idx",
    )


def _agent_right_column(ticket: dict[str, Any]) -> None:
    st.markdown("#### 3 · Draft & decide")

    hits = st.session_state.get("last_hits", [])
    cls = st.session_state.get("last_classification")
    if not cls:
        st.caption("Run the classifier on the left to get started.")
        return
    if cls.label != "support_request":
        st.caption("Ticket is on the auto-close path — no drafting needed.")
        return
    if not hits:
        st.caption("No matched playbooks yet.")
        return

    chosen_idx = st.session_state.get("chosen_hit_idx", 0)
    chosen_hit = hits[chosen_idx]
    st.caption(f"Drafting against: **{chosen_hit.playbook.title}**")

    if st.button("Generate draft", type="primary", key="btn_draft"):
        with st.spinner("Drafting reply…"):
            try:
                draft = draft_reply(
                    ticket_summary=ticket.get("summary", ""),
                    ticket_description=ticket.get("description", ""),
                    playbook=chosen_hit.playbook,
                )
                st.session_state["last_draft"] = draft
                st.session_state["draft_for"] = (ticket.get("key"), chosen_hit.playbook.id)
            except Exception as exc:
                st.error(f"Drafter failed: {exc}")
                return

    draft = st.session_state.get("last_draft")
    if not draft or st.session_state.get("draft_for") != (ticket.get("key"), chosen_hit.playbook.id):
        return

    st.markdown(
        f'{_action_pill(draft.recommended_action)} '
        f'<span class="sp-conf-label">{html.escape(draft.rationale)}</span>',
        unsafe_allow_html=True,
    )
    edited = st.text_area("Reply (edit before sending if needed)", value=draft.draft, height=320, key="draft_text")

    col_a, col_e, col_r = st.columns(3)
    with col_a:
        if st.button("Approve", use_container_width=True, key="btn_approve", type="primary"):
            feedback.record_feedback(
                ticket_id=str(ticket.get("key", "?")),
                playbook_id=chosen_hit.playbook.id,
                draft_text=draft.draft,
                final_text=edited if edited != draft.draft else None,
                status="edited" if edited != draft.draft else "approved",
            )
            st.success("Feedback logged.")
    with col_e:
        if st.button("Save edit", use_container_width=True, key="btn_edit"):
            feedback.record_feedback(
                ticket_id=str(ticket.get("key", "?")),
                playbook_id=chosen_hit.playbook.id,
                draft_text=draft.draft,
                final_text=edited,
                status="edited",
            )
            st.success("Edit logged.")
    with col_r:
        if st.button("Reject", use_container_width=True, key="btn_reject"):
            feedback.record_feedback(
                ticket_id=str(ticket.get("key", "?")),
                playbook_id=chosen_hit.playbook.id,
                draft_text=draft.draft,
                status="rejected",
            )
            st.warning("Rejection logged.")


def render_agent_tab(index: PlaybookIndex) -> None:
    tickets = _load_tickets()
    if not tickets:
        st.warning(
            f"No tickets at {config.TICKET_SAMPLE_FILE}. "
            "Drop a JSONL sample there to populate this tab."
        )
        return

    ticket = _agent_sidebar(tickets)

    # Reset per-ticket state when the selection changes.
    if st.session_state.get("agent_ticket_key") != ticket.get("key"):
        for k in ("last_classification", "last_hits", "last_draft", "chosen_hit_idx", "hits_for", "draft_for"):
            st.session_state.pop(k, None)
        st.session_state["agent_ticket_key"] = ticket.get("key")

    col_left, col_right = st.columns([1, 1], gap="large")
    with col_left:
        _agent_left_column(ticket, index)
    with col_right:
        _agent_right_column(ticket)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    _inject_theme()
    st.markdown("# Signal Pilot")
    st.caption("Support-ticket triage — retrieval + drafter + feedback log")
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
