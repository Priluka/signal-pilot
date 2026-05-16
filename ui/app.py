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
import re
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
from core.answerer import extract_cited_ids, stream_answer
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


def _render_chat_source_card(hit, cited: bool) -> None:
    """Source playbook card under the Chat answer; flags whether the answer cited it."""
    cited_badge = (
        '<span class="sp-pill sp-pill-support">cited</span>' if cited else ''
    )
    chips = _chips([c for c in [hit.playbook.ticket_class, *hit.playbook.country_focus] if c])
    st.markdown(
        '<div class="sp-card">'
        f'<div class="sp-card-title">{html.escape(hit.playbook.title)} {cited_badge}</div>'
        f'<div class="sp-card-meta"><code>{html.escape(hit.playbook.id)}</code>{chips}</div>'
        f'{confidence_bar(hit.score)}'
        f'<div class="sp-card-body">{html.escape(hit.playbook.description)}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.expander("Show full playbook"):
        st.markdown(hit.playbook.body)


def render_chat_tab(index: PlaybookIndex) -> None:
    with st.sidebar:
        st.markdown("#### Search options")
        top_k = st.slider("Playbooks to consult", 1, 5, 3, key="chat_topk")

    st.markdown("### Ask the knowledge base")
    question = st.text_area(
        "Your question",
        height=120,
        placeholder="e.g. What do I tell a Croatian customer who got a parking fine despite paying via the app?",
    )

    col_ask, col_clear = st.columns([1, 5])
    with col_ask:
        ask = st.button("Ask", type="primary", use_container_width=True)
    with col_clear:
        if st.session_state.get("chat_state") and st.button("Clear", key="chat_clear"):
            st.session_state.pop("chat_state", None)
            st.rerun()

    # Fresh question → retrieve and stream a new answer, then persist to session_state.
    if ask:
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

        playbooks = [h.playbook for h in hits]

        st.markdown("##### Answer")
        st.caption(f"Sonnet 4.6 · grounded in {len(playbooks)} playbook(s)")
        try:
            gen = stream_answer(question=question, playbooks=playbooks)
            answer_text = st.write_stream(gen) or ""
        except Exception as exc:
            st.error(f"Answer generation failed: {exc}")
            return

        cited_ids = extract_cited_ids(answer_text, playbooks)
        st.session_state["chat_state"] = {
            "question": question,
            "answer": answer_text,
            "hits": hits,
            "cited_ids": cited_ids,
        }

        # Sources panel after a fresh stream
        _render_chat_sources(hits, set(cited_ids))
        return

    # No fresh question this run — replay the last answer from session_state if any.
    state = st.session_state.get("chat_state")
    if state:
        st.markdown("##### Answer")
        st.caption(f"Sonnet 4.6 · grounded in {len(state['hits'])} playbook(s)  ·  asked: _{state['question']}_")
        st.markdown(state["answer"])
        _render_chat_sources(state["hits"], set(state["cited_ids"]))


def _render_chat_sources(hits, cited_set: set[str]) -> None:
    st.markdown("##### Sources")
    if cited_set:
        cited_codes = ", ".join(f"`{c}`" for c in cited_set)
        st.caption(f"Cited in answer: {cited_codes}")
    else:
        st.caption("No inline citations detected — answer may be ungrounded; double-check.")
    for hit in hits:
        _render_chat_source_card(hit, cited=hit.playbook.id in cited_set)


# ---------- Agent tab ------------------------------------------------------
# Per-ticket session keys — cleared whenever the ticket selection changes or
# the user clicks "Redo this ticket".
_PER_TICKET_KEYS: tuple[str, ...] = (
    "last_classification",
    "last_hits",
    "last_draft",
    "chosen_hit_idx",
    "draft_for",
    "draft_text",
    "feedback_done",
    "feedback_status",
)

_SECTION_RE = re.compile(
    r"^#{2,}\s+(?P<title>.+?)\s*\n(?P<body>.*?)(?=^#{2,}\s|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _extract_section(body: str, *needles: str) -> str:
    """First ``## Heading`` section whose title contains any of *needles*."""
    needles_lower = [n.lower() for n in needles]
    for match in _SECTION_RE.finditer(body):
        title = match.group("title").lower()
        if any(n in title for n in needles_lower):
            return match.group("body").strip()
    return ""


def _reset_per_ticket_state() -> None:
    for key in _PER_TICKET_KEYS:
        st.session_state.pop(key, None)


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


def _render_ticket_card(ticket: dict[str, Any]) -> None:
    """Ticket header card — always shown expanded, never collapsed behind an expander."""
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
        f'<div class="sp-card-body" style="white-space:pre-wrap;">{description}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _render_classification(cls) -> None:
    st.markdown(
        f'{_classification_pill(cls.label)} '
        f'<span class="sp-conf-label">conf {cls.confidence:.2f}</span>',
        unsafe_allow_html=True,
    )
    if cls.reason:
        st.caption(cls.reason)


def _render_retrieval(hits, ticket: dict[str, Any]) -> None:
    detected_lang = detect_language(_ticket_text(ticket))
    detected_country = country_from_labels(ticket.get("labels") or [])
    st.caption(
        f"Detected language: `{detected_lang or '—'}`  ·  country: `{detected_country or '—'}`"
    )
    for h in hits:
        st.markdown(
            '<div class="sp-card">'
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


def _render_playbook_source(playbook: Playbook) -> None:
    """Right-hand pane during drafting — shows where the drafter's content comes from."""
    st.markdown("##### Playbook source")
    st.caption(f"`{playbook.id}` — {playbook.title}")

    when_applies = playbook.when_applies
    flow = _extract_section(playbook.body, "Typical resolution flow", "Resolution flow")
    actions = _extract_section(playbook.body, "Typical actions")
    safety = _extract_section(playbook.body, "Safety constraints", "Risks")

    if when_applies:
        st.markdown("**When this applies**")
        st.markdown(when_applies)
    if flow:
        st.markdown("**Typical resolution flow**")
        st.markdown(flow)
    if actions:
        st.markdown("**Typical actions**")
        st.markdown(actions)
    if safety:
        with st.expander("Safety constraints / risks"):
            st.markdown(safety)


def _submit_feedback(
    *,
    ticket: dict[str, Any],
    playbook_id: str,
    draft_text: str,
    final_text: str | None,
    status: str,
) -> None:
    feedback.record_feedback(
        ticket_id=str(ticket.get("key", "?")),
        playbook_id=playbook_id,
        draft_text=draft_text,
        final_text=final_text,
        status=status,  # type: ignore[arg-type]
    )
    st.session_state["feedback_done"] = True
    st.session_state["feedback_status"] = status


def _render_draft_panel(ticket: dict[str, Any], hits) -> None:
    """Manual 'Generate draft' button → side-by-side draft + playbook source + decision row."""
    chosen_idx = st.session_state.get("chosen_hit_idx", 0)
    chosen_hit = hits[chosen_idx]
    st.caption(f"Drafting against: **{chosen_hit.playbook.title}**")

    if st.button("Generate draft", type="primary", key="btn_draft"):
        with st.spinner("Drafting reply…"):
            try:
                st.session_state["last_draft"] = draft_reply(
                    ticket_summary=ticket.get("summary", ""),
                    ticket_description=ticket.get("description", ""),
                    playbook=chosen_hit.playbook,
                )
                st.session_state["draft_for"] = (ticket.get("key"), chosen_hit.playbook.id)
                # Drop any stale edit buffer from a previous draft.
                st.session_state.pop("draft_text", None)
            except Exception as exc:
                st.error(f"Drafter failed: {exc}")
                return

    draft = st.session_state.get("last_draft")
    if not draft or st.session_state.get("draft_for") != (ticket.get("key"), chosen_hit.playbook.id):
        return

    col_draft, col_source = st.columns([1.2, 1], gap="large")

    with col_draft:
        st.markdown("##### Draft reply")
        st.markdown(
            f'{_action_pill(draft.recommended_action)} '
            f'<span class="sp-conf-label">{html.escape(draft.rationale)}</span>',
            unsafe_allow_html=True,
        )
        edited = st.text_area(
            "Reply (edit before sending if needed)",
            value=draft.draft,
            height=340,
            key="draft_text",
        )

        st.markdown("##### Decide")
        col_a, col_e, col_r = st.columns(3)
        with col_a:
            if st.button("Approve & send", use_container_width=True, key="btn_approve", type="primary"):
                _submit_feedback(
                    ticket=ticket,
                    playbook_id=chosen_hit.playbook.id,
                    draft_text=draft.draft,
                    final_text=edited if edited != draft.draft else None,
                    status="edited" if edited != draft.draft else "approved",
                )
                st.rerun()
        with col_e:
            if st.button("Save edit", use_container_width=True, key="btn_edit"):
                _submit_feedback(
                    ticket=ticket,
                    playbook_id=chosen_hit.playbook.id,
                    draft_text=draft.draft,
                    final_text=edited,
                    status="edited",
                )
                st.rerun()
        with col_r:
            if st.button("Reject", use_container_width=True, key="btn_reject"):
                _submit_feedback(
                    ticket=ticket,
                    playbook_id=chosen_hit.playbook.id,
                    draft_text=draft.draft,
                    final_text=None,
                    status="rejected",
                )
                st.rerun()

    with col_source:
        _render_playbook_source(chosen_hit.playbook)


def _render_feedback_done(ticket: dict[str, Any], tickets: list[dict[str, Any]]) -> None:
    """Confirmation banner + next-ticket / redo controls after a feedback decision."""
    status = st.session_state.get("feedback_status", "logged")
    cur_idx = st.session_state.get("agent_ticket_idx", 0)
    has_next = cur_idx + 1 < len(tickets)

    if status == "rejected":
        st.warning(f"Rejection logged for **{ticket.get('key')}** — no reply sent.")
    elif status == "edited":
        st.success(f"Edited reply logged for **{ticket.get('key')}**.")
    else:
        st.success(f"Reply approved for **{ticket.get('key')}**.")

    col_next, col_redo = st.columns([1, 1])
    with col_next:
        if has_next:
            if st.button("Next ticket", type="primary", use_container_width=True, key="btn_next"):
                st.session_state["_advance_to_next"] = True
                st.rerun()
        else:
            st.caption("No more tickets in the sample.")
    with col_redo:
        if st.button("Redo this ticket", use_container_width=True, key="btn_redo"):
            _reset_per_ticket_state()
            st.session_state.pop("agent_ticket_key", None)
            st.rerun()


def render_agent_tab(index: PlaybookIndex) -> None:
    tickets = _load_tickets()
    if not tickets:
        st.warning(
            f"No tickets at {config.TICKET_SAMPLE_FILE}. "
            "Drop a JSONL sample there to populate this tab."
        )
        return

    # Honor a pending "Next ticket" navigation BEFORE the sidebar widget renders,
    # otherwise Streamlit will refuse to mutate the widget-bound session_state key.
    if st.session_state.pop("_advance_to_next", False):
        cur_idx = st.session_state.get("agent_ticket_idx", 0)
        st.session_state["agent_ticket_idx"] = min(cur_idx + 1, len(tickets) - 1)
        _reset_per_ticket_state()

    ticket = _agent_sidebar(tickets)

    # Reset per-ticket state when the selection changes.
    if st.session_state.get("agent_ticket_key") != ticket.get("key"):
        _reset_per_ticket_state()
        st.session_state["agent_ticket_key"] = ticket.get("key")

    _render_ticket_card(ticket)

    # If the user has already decided on this ticket, show the confirmation panel
    # and the next-ticket controls — don't re-run classify/retrieve/draft.
    if st.session_state.get("feedback_done"):
        _render_feedback_done(ticket, tickets)
        return

    # --- Step 1: auto-classify ---------------------------------------------
    st.markdown("##### Classification")
    if "last_classification" not in st.session_state:
        with st.spinner("Classifying ticket…"):
            try:
                st.session_state["last_classification"] = classify_ticket(
                    summary=ticket.get("summary", ""),
                    description=ticket.get("description", ""),
                    reporter_email=ticket.get("reporter_email"),
                    labels=ticket.get("labels") or [],
                )
            except Exception as exc:
                st.error(f"Classifier failed: {exc}")
                return
    cls = st.session_state["last_classification"]
    _render_classification(cls)

    if cls.label != "support_request":
        st.info(
            f"Auto-close path: classified as `{cls.label}` — no reply needed. "
            "Move to the next ticket from the sidebar."
        )
        return

    # --- Step 2: auto-retrieve ---------------------------------------------
    st.markdown("##### Matched playbooks")
    if "last_hits" not in st.session_state:
        with st.spinner("Retrieving playbooks…"):
            try:
                hits = retrieve(
                    index,
                    _ticket_text(ticket),
                    labels=ticket.get("labels") or [],
                    ticket_class=None,
                )
                st.session_state["last_hits"] = hits
                st.session_state["chosen_hit_idx"] = 0
            except Exception as exc:
                st.error(f"Retrieval failed: {exc}")
                return

    hits = st.session_state.get("last_hits", [])
    if not hits:
        st.info("No playbook matched.")
        return

    _render_retrieval(hits, ticket)

    # --- Step 3: draft (manual trigger) + decide ---------------------------
    st.markdown("##### Draft")
    _render_draft_panel(ticket, hits)


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
