"""Pydantic response models for the FastAPI backend."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlaybookSummary(BaseModel):
    """Lightweight playbook view for list endpoints."""

    id: str
    title: str
    description: str
    category: str
    ticket_class: str
    issue_category: str
    languages: list[str]
    country_focus: list[str]
    resolution_pattern: str
    status: str = "active"
    extraction_confidence: float | None = None
    cluster_size: int | None = None
    project_keys: list[str] = Field(default_factory=list)


class TicketActionRow(BaseModel):
    """One row of a playbook's actions table (parsed from markdown)."""

    what: str
    who: str
    tool: str
    duration: str


class EvidenceQuote(BaseModel):
    """One evidence-tickets bullet from the playbook body."""

    ticket_id: str
    language: str | None = None
    quote: str


class ROIStrategy(BaseModel):
    """One automation/intervention strategy and its estimated hours saved."""

    hours_midpoint: float | None = None
    hours_range_low: float | None = None
    hours_range_high: float | None = None
    confidence_tier: str | None = None


class ROIBreakdown(BaseModel):
    """The four ROI strategies plus the baseline annual active-work estimate."""

    baseline_active_hours: float | None = None
    baseline_confidence_tier: str | None = None
    agent_assist: ROIStrategy | None = None
    product_fix: ROIStrategy | None = None
    deflection: ROIStrategy | None = None
    autonomous_resolve: ROIStrategy | None = None


class RelatedPlaybookOut(BaseModel):
    """Lookup result for a related-playbook reference."""

    id: str
    title: str
    description: str
    issue_category: str = ""
    status: str = "active"


class PlaybookDetail(PlaybookSummary):
    """Full playbook view for the viewer pane."""

    when_applies: str = ""
    resolution_flow: str = ""
    typical_actions: str = ""
    typical_actions_rows: list[TicketActionRow] = Field(default_factory=list)
    risks: str = ""
    body: str = ""
    resolution_steps: list[str] = Field(default_factory=list)
    evidence_tickets: list[str] = Field(default_factory=list)
    evidence_quotes: list[EvidenceQuote] = Field(default_factory=list)
    canonical_examples: list[str] = Field(default_factory=list)
    related_playbooks: list[str] = Field(default_factory=list)
    related_playbooks_resolved: list[RelatedPlaybookOut] = Field(default_factory=list)
    created: str | None = None
    updated: str | None = None
    correction_count: int = 0
    sample_size_used: int | None = None
    frequency_per_month: float | None = None
    median_resolution_minutes: float | None = None
    cluster_id: str | None = None
    roi: ROIBreakdown | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CountedName(BaseModel):
    name: str
    count: int


class CategoriesResponse(BaseModel):
    total: int
    ticket_classes: list[CountedName]
    issue_categories: list[CountedName]
    by_ticket_class: dict[str, list[CountedName]] = Field(default_factory=dict)


# --- Discovery report ------------------------------------------------------
class DiscoveryCategoryEntry(BaseModel):
    name: str
    count: int
    playbook_titles: list[str] = Field(default_factory=list)


class DiscoveryCountryEntry(BaseModel):
    code: str
    count: int


class DiscoveryROISummary(BaseModel):
    baseline_hours: float
    agent_assist_hours: float
    autonomous_hours: float


class DiscoveryGap(BaseModel):
    category: str
    count: int


class DiscoveryTopPlaybook(BaseModel):
    id: str
    title: str
    cluster_size: int


class DiscoveryQuality(BaseModel):
    min: float | None = None
    max: float | None = None
    avg: float | None = None
    low_confidence_count: int = 0


class DiscoveryReport(BaseModel):
    total_playbooks: int
    total_tickets_covered: int
    avg_confidence: float | None = None
    categories: list[DiscoveryCategoryEntry] = Field(default_factory=list)
    countries: list[DiscoveryCountryEntry] = Field(default_factory=list)
    languages: list[CountedName] = Field(default_factory=list)
    roi_summary: DiscoveryROISummary
    gaps: list[DiscoveryGap] = Field(default_factory=list)
    top_playbooks: list[DiscoveryTopPlaybook] = Field(default_factory=list)
    quality: DiscoveryQuality


# --- Knowledge graph -------------------------------------------------------
class GraphNode(BaseModel):
    id: str
    title: str
    ticket_class: str
    issue_category: str
    cluster_size: int | None = None
    extraction_confidence: float | None = None
    status: str = "active"
    degree: int = 0


class GraphEdge(BaseModel):
    source: str
    target: str


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


# --- Tickets ---------------------------------------------------------------
class TicketSummary(BaseModel):
    key: str
    summary: str
    status: str = ""
    status_category: str | None = None
    priority: str | None = None
    labels: list[str] = Field(default_factory=list)
    reporter_email: str | None = None
    reporter_name: str | None = None
    created_at: str | None = None
    resolved_at: str | None = None


class TicketDetail(TicketSummary):
    description: str = ""
    assignee_name: str | None = None
    project_key: str | None = None
    issue_type: str | None = None
    resolution: str | None = None
    resolution_minutes: int | None = None
    comment_count_total: int = 0


# --- Agent (classify / retrieve / draft) -----------------------------------
class ClassifyRequest(BaseModel):
    summary: str
    description: str = ""
    reporter_email: str | None = None
    labels: list[str] = Field(default_factory=list)


class ClassifyResponse(BaseModel):
    label: str
    confidence: float
    reason: str


class RetrieveRequest(BaseModel):
    summary: str
    description: str = ""
    labels: list[str] = Field(default_factory=list)
    ticket_class: str | None = None
    top_k: int = 3


class RetrievalHitOut(BaseModel):
    playbook_id: str
    title: str
    description: str
    score: float
    rank: int
    ticket_class: str
    issue_category: str
    country_focus: list[str]
    languages: list[str]
    status: str = "active"
    extraction_confidence: float | None = None
    project_keys: list[str] = Field(default_factory=list)


class RetrieveResponse(BaseModel):
    hits: list[RetrievalHitOut]
    detected_language: str | None = None
    detected_country: str | None = None


class DraftRequest(BaseModel):
    ticket_summary: str
    ticket_description: str = ""
    playbook_id: str


class DraftResponse(BaseModel):
    draft: str
    recommended_action: str
    rationale: str


class AgentSessionDetail(BaseModel):
    ticket_id: str
    classification: ClassifyResponse | None = None
    retrieval: RetrieveResponse | None = None
    draft: DraftResponse | None = None
    draft_playbook_id: str | None = None
    edited_text: str | None = None
    feedback_status: str | None = None
    derived_status: str = "pending"
    updated_at: str
    started_at: str | None = None
    classified_at: str | None = None
    retrieved_at: str | None = None
    drafted_at: str | None = None
    feedback_at: str | None = None
    # Set when autonomous mode posted the final reply directly to the
    # source system (Jira). When non-null the operator UI hides the
    # Approve/Edit/Reject row and shows an 'auto-resolved' banner instead.
    auto_posted_at: str | None = None
    # Effective mode at the time this ticket was processed — drives the
    # per-ticket mode badge in the inbox list and the detail view.
    processed_mode: str | None = None
    # Convenience: lets the frontend render a 'Open in Jira' link without
    # having to fetch the connection separately. Populated from JIRA_URL.
    jira_browse_url: str | None = None


class AgentSessionSummary(BaseModel):
    """Compact per-ticket workflow state for the Agent Feed inbox list."""

    ticket_id: str
    derived_status: str
    classification_label: str | None = None
    classification_confidence: float | None = None
    draft_playbook_id: str | None = None
    draft_playbook_title: str | None = None
    recommended_action: str | None = None
    feedback_status: str | None = None
    updated_at: str
    drafted_at: str | None = None
    feedback_at: str | None = None
    processed_mode: str | None = None


class BatchStatus(BaseModel):
    running: bool
    processed: int
    total: int
    started_at: str | None = None
    finished_at: str | None = None
    current_ticket: str | None = None
    errors: list[dict[str, str]] = Field(default_factory=list)


class AgentMetrics(BaseModel):
    total: int
    processed: int
    needs_review: int = 0
    auto_drafted: int = 0
    auto_resolved: int = 0
    escalated: int = 0
    skipped: int = 0
    approved: int = 0
    rejected: int = 0
    in_progress: int = 0
    pending: int = 0
    approval_rate: float = 0.0
    avg_confidence: float = 0.0


class SuggestionDiff(BaseModel):
    """Content of a suggestion (old/new text) carried on activity events
    so the Activity Log can show the actual diff inline, not just the
    metadata."""

    old: str | None = None
    new: str | None = None


class AgentActivityEvent(BaseModel):
    """One agent step or operator decision — derived from agent_sessions
    timestamps and rendered as a single row in the Activity log."""

    timestamp: str
    ticket_id: str
    event_type: str  # classified | retrieved | drafted | approved | edited | rejected | skipped | suggestion_created | suggestion_accepted | suggestion_rejected
    detail: str
    # Populated only for suggestion_* events so the Activity Log can
    # render the actual content change below the metadata line.
    diff: SuggestionDiff | None = None


# --- Chat ------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    top_k: int = 3


class ChatSessionSummary(BaseModel):
    id: int
    question: str
    top_k: int
    timestamp: str
    source_count: int = 0
    citation_count: int = 0
    status: str = "done"


class CitationEntry(BaseModel):
    """One row of the citation index — every ``[id]`` that appears in the
    answer is resolved against the full playbook corpus (not just the
    retrieved top-K) and returned as one of these.

    ``in_topk=True`` means the model anchored on a source we actually
    showed it; ``False`` means it cited a playbook from outside the
    retrieved set (we'd never have shown it that source, but the
    citation still resolves to a real playbook).

    ``exists=False`` means the id wasn't found anywhere in the corpus —
    the model hallucinated it. The UI should suppress these entirely.
    """
    playbook_id: str
    title: str
    description: str = ""
    in_topk: bool = False
    exists: bool = True


class ChatSessionDetail(ChatSessionSummary):
    answer: str
    hits: list[RetrievalHitOut] = Field(default_factory=list)
    cited_ids: list[str] = Field(default_factory=list)
    citation_index: list[CitationEntry] = Field(default_factory=list)
    error_message: str | None = None


# --- Feedback --------------------------------------------------------------
class FeedbackRequest(BaseModel):
    ticket_id: str
    playbook_id: str
    draft_text: str
    final_text: str | None = None
    status: str  # 'approved' | 'edited' | 'rejected'


class FeedbackRecordOut(BaseModel):
    id: int
    ticket_id: str
    playbook_id: str
    draft_text: str
    final_text: str | None
    status: str
    timestamp: str


class FeedbackStats(BaseModel):
    approved: int = 0
    edited: int = 0
    rejected: int = 0
    total: int = 0


# --- Suggestions -----------------------------------------------------------
class SuggestionRequest(BaseModel):
    playbook_id: str
    section: str
    step_number: int | None = None
    old_text: str = ""
    new_text: str = ""
    author: str = "anonymous"
    # New as of v0.8: suggestion type. Defaults to 'edit' so older clients
    # keep working without changes.
    type: str = "edit"  # 'edit' | 'add' | 'remove'
    # Only used by type='add'. Format: 'end' or 'after:N' (1-indexed).
    position: str | None = None


class SuggestionRecordOut(BaseModel):
    id: int
    playbook_id: str
    section: str
    step_number: int | None
    old_text: str
    new_text: str
    author: str
    status: str
    timestamp: str
    decided_at: str | None = None
    type: str = "edit"
    position: str | None = None


class SuggestionStats(BaseModel):
    pending: int = 0
    accepted: int = 0
    rejected: int = 0
    total: int = 0


# --- Jira ------------------------------------------------------------------
class JiraTicketSummary(TicketSummary):
    """Identical shape to TicketSummary — separate class only for the OpenAPI tag."""


class JiraTicketDetail(TicketDetail):
    pass


class JiraCommentRequest(BaseModel):
    issue_key: str
    body: str


class JiraCommentResponse(BaseModel):
    id: str
    issue_key: str
    created: str | None = None
    author: str | None = None


# --- Agent config / mode --------------------------------------------------
class AgentConfig(BaseModel):
    mode: str  # 'shadow' | 'assisted' | 'autonomous'
    confidence_threshold: float


class AgentConfigUpdate(BaseModel):
    mode: str | None = None
    confidence_threshold: float | None = None


class PlaybookModeUpdate(BaseModel):
    # ``mode = None`` clears the per-playbook override so it follows the
    # global mode again.
    mode: str | None = None


class PlaybookModeRow(BaseModel):
    playbook_id: str
    title: str
    ticket_class: str
    mode: str  # effective mode (override or global)
    is_override: bool
    sample_count: int
    approved_count: int
    edited_count: int
    rejected_count: int
    approve_rate: float | None = None
    avg_confidence: float | None = None


class AgentOverview(BaseModel):
    name: str = "bMove Support Agent"
    status: str = "Active"
    mode: str
    confidence_threshold: float
    source_label: str  # e.g. "Jira · KAN (teamoraapp.atlassian.net)"
    playbooks_loaded: int
    processed: int
    approval_rate: float | None
    approved_count: int
    rejected_count: int
    avg_confidence: float | None
    uptime_since: str | None  # earliest agent_sessions timestamp


class JiraConnectionStatus(BaseModel):
    configured: bool
    url: str | None = None
    email: str | None = None
    project: str | None = None
    token_masked: str | None = None
    reachable: bool | None = None
    detail: str | None = None
