"""Jira skills — wrappers around ``core.jira_client`` calls.

Importing this package side-effects: each skill module registers itself
into ``core.skills.REGISTRY`` at import time via the ``@register`` decorator.
"""
from core.skills.jira import (  # noqa: F401  — side-effect: register skills
    add_internal_comment,
    add_public_comment,
    get_history,
    transition,
)

__all__ = [
    "add_internal_comment",
    "add_public_comment",
    "get_history",
    "transition",
]
