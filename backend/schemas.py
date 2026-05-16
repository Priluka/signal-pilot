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
    created: str | None = None
    updated: str | None = None
    correction_count: int = 0
    frequency_per_month: float | None = None
    median_resolution_minutes: float | None = None
    cluster_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CountedName(BaseModel):
    name: str
    count: int


class CategoriesResponse(BaseModel):
    total: int
    ticket_classes: list[CountedName]
    issue_categories: list[CountedName]
    by_ticket_class: dict[str, list[CountedName]] = Field(default_factory=dict)
