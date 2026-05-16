"""FastAPI entry point for signal-pilot.

Run with:
    .venv/bin/uvicorn backend.main:app --reload --port 8000

Loads ``.env`` (for ``ANTHROPIC_API_KEY`` etc.), parses all playbooks at
startup, registers routers, and opens CORS for the local Vite dev server.
The embedding index is built lazily — only when an endpoint that needs
retrieval is hit — so the API is responsive immediately for knowledge
endpoints.
"""
from __future__ import annotations

import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing config so os.environ.get() picks up the values.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Make the repo root importable so ``core.*`` resolves under ``uvicorn``.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from core.retrieval import discover_playbook_paths, load_playbook

from .routers import agent, categories, chat, feedback, playbooks, tickets


def _load_ticket_sample(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


@asynccontextmanager
async def lifespan(app: FastAPI):
    paths = discover_playbook_paths(config.PLAYBOOKS_DIR)
    app.state.playbooks = [load_playbook(p) for p in paths]
    app.state.tickets = _load_ticket_sample(config.TICKET_SAMPLE_FILE)
    app.state.index = None  # built lazily on first retrieval request
    yield


app = FastAPI(
    title="Signal Pilot API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "playbooks_loaded": len(app.state.playbooks) if app.state.playbooks else 0,
        "tickets_loaded": len(app.state.tickets) if app.state.tickets else 0,
        "index_built": app.state.index is not None,
    }


app.include_router(playbooks.router)
app.include_router(categories.router)
app.include_router(tickets.router)
app.include_router(agent.router)
app.include_router(chat.router)
app.include_router(feedback.router)
