"""Skill base class.

A Skill wraps one external action (a Jira comment, an IGeus lookup, etc.).
It carries everything Claude needs to call it (name, description, schema)
plus everything we need to execute it safely (is_write flag, audit hooks).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class SkillResult:
    """Returned by every ``Skill.execute``. Serialized into the audit log."""
    ok: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class Skill(ABC):
    """Abstract base for every Skill.

    Subclasses must set the four class-level attributes and implement
    ``execute``. The ``to_tool_spec`` method produces the dict shape the
    Anthropic ``tool_use`` API expects.
    """

    # Set by subclass — Anthropic sees these
    name: ClassVar[str]
    description: ClassVar[str]
    input_schema: ClassVar[dict[str, Any]]

    # Phase 12.7 — optional JSON schema describing the SUCCESSFUL
    # response shape (``SkillResult.data``). When set, the agent loop
    # validates the dict against this schema after execute() returns;
    # malformed responses get treated as a skill error and a clean
    # message goes to the LLM instead of garbage. Default ``None``
    # keeps every existing skill working unchanged — opt-in per skill.
    output_schema: ClassVar[dict[str, Any] | None] = None

    # Set by subclass — used by validator/planner
    is_write: ClassVar[bool]

    @abstractmethod
    def execute(self, **params: Any) -> SkillResult:
        """Run the skill. Params are already schema-validated by the caller."""

    @classmethod
    def to_tool_spec(cls) -> dict[str, Any]:
        """Anthropic ``tool_use`` dict — what we send to Claude."""
        return {
            "name": cls.name,
            "description": cls.description,
            "input_schema": cls.input_schema,
        }
