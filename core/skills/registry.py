"""Skill registry — single source of truth for available skills.

A skill registers itself via the ``@register`` decorator at import time.
The planner uses ``tools_for_playbook`` to filter the registry down to
the skills allow-listed by the matched playbook before sending the
tool list to Claude.
"""
from __future__ import annotations

from typing import Any

from core.skills.base import Skill

REGISTRY: dict[str, type[Skill]] = {}


def register(cls: type[Skill]) -> type[Skill]:
    """Decorator — adds the skill class to the global registry by ``name``."""
    if cls.name in REGISTRY:
        raise ValueError(f"Skill {cls.name!r} already registered")
    REGISTRY[cls.name] = cls
    return cls


def get_skill(name: str) -> Skill | None:
    """Instantiate a registered skill by name, or return ``None`` if unknown."""
    cls = REGISTRY.get(name)
    return cls() if cls else None


def tools_for_playbook(allowed_skills: list[str]) -> list[dict[str, Any]]:
    """Return Anthropic ``tool_use`` specs for skills allow-listed by a playbook.

    Unknown names are silently dropped — typo in a playbook should not crash
    the planner, but the missing skill simply won't be available to Claude.
    """
    out: list[dict[str, Any]] = []
    for name in allowed_skills:
        cls = REGISTRY.get(name)
        if cls is not None:
            out.append(cls.to_tool_spec())
    return out
