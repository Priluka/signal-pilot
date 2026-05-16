"""Shared FastAPI dependencies.

Holds the parsed-playbook list, the lazily-built retrieval index, and the
loaded ticket sample in ``app.state`` so route handlers can pull them via
``Depends``.
"""
from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request

from core.retrieval import Playbook, PlaybookIndex


def get_playbooks(request: Request) -> list[Playbook]:
    playbooks: list[Playbook] | None = getattr(request.app.state, "playbooks", None)
    if playbooks is None:
        raise HTTPException(status_code=503, detail="Playbooks not loaded yet")
    return playbooks


def get_playbook_by_id(request: Request, playbook_id: str) -> Playbook:
    for pb in get_playbooks(request):
        if pb.id == playbook_id:
            return pb
    raise HTTPException(status_code=404, detail=f"Playbook {playbook_id!r} not found")


def get_playbook_index(request: Request) -> PlaybookIndex:
    """Build the embedding index on first call, then reuse the cached one."""
    index: PlaybookIndex | None = getattr(request.app.state, "index", None)
    if index is None:
        from core.retrieval import build_index

        index = build_index()
        request.app.state.index = index
    return index


def get_tickets(request: Request) -> list[dict[str, Any]]:
    tickets: list[dict[str, Any]] | None = getattr(request.app.state, "tickets", None)
    if tickets is None:
        raise HTTPException(status_code=503, detail="Tickets not loaded yet")
    return tickets
