"""Central configuration for signal-pilot.

All tunables live here so swapping a model, a path, or a provider is a one-file change.
Environment variables override defaults — see README for a full list.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR: Path = Path(__file__).resolve().parent
DATA_DIR: Path = ROOT_DIR / "data"
PLAYBOOKS_DIR: Path = DATA_DIR / "playbooks"
TICKETS_DIR: Path = DATA_DIR / "tickets"
CACHE_DIR: Path = DATA_DIR / "cache"
FEEDBACK_DB_PATH: Path = ROOT_DIR / "feedback.sqlite3"

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Embeddings — swap provider by changing EMBEDDING_PROVIDER (local|voyage).
EMBEDDING_PROVIDER: str = os.environ.get("EMBEDDING_PROVIDER", "local")
EMBEDDING_MODEL_LOCAL: str = os.environ.get("EMBEDDING_MODEL_LOCAL", "BAAI/bge-m3")
EMBEDDING_MODEL_VOYAGE: str = os.environ.get("EMBEDDING_MODEL_VOYAGE", "voyage-3")
EMBEDDING_DEVICE: str = os.environ.get("EMBEDDING_DEVICE", "cpu")
EMBEDDING_CACHE_PATH: Path = CACHE_DIR / "playbook_embeddings.npz"

# Retrieval
TOP_K_RETRIEVAL: int = int(os.environ.get("TOP_K_RETRIEVAL", "3"))
MIN_RETRIEVAL_CONFIDENCE: float = float(os.environ.get("MIN_RETRIEVAL_CONFIDENCE", "0.25"))

# Claude API — drafter + classifier
ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
CLASSIFIER_MODEL: str = os.environ.get("CLASSIFIER_MODEL", "claude-haiku-4-5-20251001")
DRAFTER_MODEL: str = os.environ.get("DRAFTER_MODEL", "claude-sonnet-4-6")
CLASSIFIER_MAX_TOKENS: int = 256
DRAFTER_MAX_TOKENS: int = 1500

# Ticket sample for the Agent tab
TICKET_SAMPLE_FILE: Path = TICKETS_DIR / "sample.jsonl"
