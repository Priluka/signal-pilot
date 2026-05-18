"""Shared FastAPI dependencies.

Holds the parsed-playbook list, the lazily-built retrieval index, and the
loaded ticket sample in ``app.state`` so route handlers can pull them via
``Depends``.
"""
from __future__ import annotations

import threading
from typing import Any

from fastapi import HTTPException, Request

from core.retrieval import Playbook, PlaybookIndex


# Guards build_index so concurrent first-callers don't all race to build a
# separate copy — that race exhausted the FastAPI worker thread pool when
# the Inbox fired five requests at once.
_index_build_lock = threading.Lock()


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
    """Build the embedding index on first call, then reuse the cached one.

    Concurrent first-callers (the Inbox alone fires 5–6 requests on mount)
    must NOT each race to build a separate copy — that pegged all FastAPI
    worker threads on parallel BGE-m3 builds and the whole backend
    appeared to hang. The lock funnels the build through a single thread;
    everyone else waits ~5 s for the cached value.
    """
    index: PlaybookIndex | None = getattr(request.app.state, "index", None)
    if index is not None:
        return index
    with _index_build_lock:
        index = getattr(request.app.state, "index", None)
        if index is not None:
            return index
        from core.retrieval import build_index

        index = build_index()
        request.app.state.index = index
        return index


def get_tickets(request: Request) -> list[dict[str, Any]]:
    tickets: list[dict[str, Any]] | None = getattr(request.app.state, "tickets", None)
    if tickets is None:
        raise HTTPException(status_code=503, detail="Tickets not loaded yet")
    return tickets
