"""Skill: ``search_playbooks``.

Lets the agent retrieve additional domain context mid-conversation when
the operator's question drifts outside the playbook that was initially
matched. Without this, a long chat that started about parking refunds
but veers into B2B invoicing would have no way to acquire the new
context — the agent would be stuck improvising from priors.

This is THE skill that turns the chat from 'agent with memory' into
'agent with research' — Claude Code uses an analogous primitive (its
filesystem search tools) for the same purpose. Operators don't have to
restart the conversation to look up something else; the agent does it
in-flow.

Read-only, auto-execute, no HITL. Underneath it's just a thin wrapper
around ``core.retrieval.retrieve`` with a lazily-built index cache so
the cold-start hit only lands once per process.
"""
from __future__ import annotations

from typing import Any

from core.skills.base import Skill, SkillResult
from core.skills.registry import register


# Module-level cache. First call triggers ``build_index`` (reads
# embedding cache from disk on warm starts, hits Voyage on cold).
# Invalidated by ``invalidate_cache`` so the playbook-reload admin
# endpoint can refresh after operators edit playbook YAML at runtime.
_INDEX_CACHE: Any = None


def set_cached_index(index: Any) -> None:
    """Inject an already-built index from the backend lifespan so
    ``search_playbooks`` shares the same one the HTTP retrieval path
    uses. Without this the skill would lazily build its OWN index on
    first invocation — and after a playbook edit invalidates the .npz
    signature, that build means a cold Voyage embed run (~3 min on
    free-tier rate limits) which trips the 30 s skill timeout.
    Backend calls this once at startup and again after every
    ``/admin/playbooks/reload``."""
    global _INDEX_CACHE
    _INDEX_CACHE = index


def _get_index() -> Any:
    global _INDEX_CACHE
    if _INDEX_CACHE is None:
        from core.retrieval import build_index

        _INDEX_CACHE = build_index()
    return _INDEX_CACHE


def invalidate_cache() -> None:
    """Drop the cached index. Called by the playbook-reload admin path
    so the next ``search_playbooks`` call picks up edits."""
    global _INDEX_CACHE
    _INDEX_CACHE = None


@register
class SearchPlaybooks(Skill):
    name = "search_playbooks"

    description = (
        "Search the knowledge base of internal support playbooks. Use "
        "when the conversation has shifted to a topic the originally "
        "matched playbook doesn't cover (e.g. operator asks about a "
        "B2B invoice issue mid-way through a refund conversation). "
        "Returns up to top_k playbook hits — each carries title, "
        "description, score, and the relevant section of body text. "
        "After getting hits, summarise the relevant guidance to the "
        "operator; don't dump the raw JSON."
    )

    is_write = False

    input_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "Natural-language search query. Be specific — "
                    "'B2B Croatian invoice request' beats 'invoice'."
                ),
            },
            "top_k": {
                "type": "integer",
                "description": "How many playbooks to return. Default 3, max 5.",
                "minimum": 1,
                "maximum": 5,
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    }

    def execute(self, **params: Any) -> SkillResult:
        query = (params.get("query") or "").strip()
        if not query:
            return SkillResult(ok=False, error="query is required")
        top_k = int(params.get("top_k") or 3)
        top_k = max(1, min(5, top_k))

        try:
            index = _get_index()
            from core.retrieval import (
                country_from_text,
                detect_language,
                retrieve,
            )

            hits = retrieve(
                index,
                query,
                labels=None,
                ticket_class=None,
                top_k=top_k,
            )
        except Exception as exc:  # noqa: BLE001
            return SkillResult(
                ok=False, error=f"retrieval_failed: {exc}"
            )

        # Detect language + country for diagnostic context — useful for
        # the agent to know whether retrieval was biased by signals it
        # didn't explicitly ask for.
        lang = detect_language(query)
        country = country_from_text(query)

        results = []
        for h in hits:
            pb = h.playbook
            # Short, useful snippets. Bigger sections (resolution_steps,
            # full body) stay out — the agent can summarise from the
            # title + description + when_applies; if it really needs
            # more, we can add a get_playbook(id) skill in v2.
            when_applies = (pb.when_applies or "").strip()
            if len(when_applies) > 600:
                when_applies = when_applies[:600].rstrip() + "…"
            description = (pb.description or "").strip()
            if len(description) > 400:
                description = description[:400].rstrip() + "…"
            results.append(
                {
                    "playbook_id": pb.id,
                    "title": pb.title,
                    "description": description,
                    "when_applies": when_applies,
                    "score": round(float(h.score), 3),
                    "ticket_class": pb.metadata.get("ticket_class"),
                    "issue_category": pb.metadata.get("issue_category"),
                    "country_focus": pb.metadata.get("country_focus") or [],
                }
            )

        return SkillResult(
            ok=True,
            data={
                "query": query,
                "top_k": top_k,
                "detected_language": lang,
                "detected_country": country,
                "total_hits": len(results),
                "hits": results,
            },
        )
