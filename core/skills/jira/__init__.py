"""Jira skills — wrappers around ``core.jira_client`` calls.

Importing this package side-effects: each skill module registers itself
into ``core.skills.REGISTRY`` at import time via the ``@register`` decorator.
"""
from core.skills.jira import add_internal_comment  # noqa: F401  (side-effect: registers skill)

__all__ = ["add_internal_comment"]
