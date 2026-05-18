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


# --- Chat ------------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    top_k: int = 3


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
    old_text: str
    new_text: str
    author: str = "anonymous"


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
