"""Playbook indexing and filtered retrieval.

Loads markdown playbooks with YAML frontmatter from ``config.PLAYBOOKS_DIR``,
embeds the searchable surface (title + description + "When this applies"
section), persists vectors to an .npz cache keyed by file mtime, and exposes
``retrieve()`` — language- and country-filtered cosine top-k.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
import yaml

import config
from core.embeddings import EmbeddingProvider, get_embedding_provider


# Files that live in the playbooks tree but are not playbooks.
_NON_PLAYBOOK_BASENAMES = {"_index.md", "README.md"}

# Map of free-text country tokens (commonly seen in Jira labels) to ISO codes.
_COUNTRY_TOKEN_TO_ISO: dict[str, str] = {
    "croatia": "hr",
    "croatian": "hr",
    "hr": "hr",
    "italy": "it",
    "italian": "it",
    "it": "it",
    "austria": "at",
    "austrian": "at",
    "at": "at",
    "slovakia": "sk",
    "slovak": "sk",
    "sk": "sk",
    "germany": "de",
    "german": "de",
    "de": "de",
}

_SECTION_RE = re.compile(
    r"^#{2,}\s+(?P<title>.+?)\s*\n(?P<body>.*?)(?=^#{2,}\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_FRONTMATTER_RE = re.compile(r"^---\n(?P<yaml>.*?)\n---\n(?P<body>.*)$", re.DOTALL)


def extract_section(body: str, *needles: str) -> str:
    """Return the body of the first ``## Heading`` (any level ≥2) whose title
    contains any of *needles* (case-insensitive). Empty string if no match.
    """
    needles_lower = [n.lower() for n in needles]
    for match in _SECTION_RE.finditer(body):
        title = match.group("title").lower()
        if any(n in title for n in needles_lower):
            return match.group("body").strip()
    return ""


@dataclass
class Playbook:
    """One markdown playbook, parsed."""

    id: str
    path: Path
    title: str
    description: str
    category: str
    ticket_class: str
    issue_category: str
    languages: list[str]
    country_focus: list[str]
    resolution_pattern: str
    when_applies: str
    resolution_flow: str
    typical_actions: str
    risks: str
    body: str
    raw: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def search_text(self) -> str:
        """The concatenated surface we embed for retrieval."""
        parts = [self.title, self.description]
        if self.when_applies:
            parts.append(self.when_applies)
        return "\n\n".join(p for p in parts if p)


@dataclass
class RetrievalHit:
    """A retrieval result, ranked."""

    playbook: Playbook
    score: float
    rank: int


def _parse_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        raise ValueError("Missing or malformed YAML frontmatter")
    meta = yaml.safe_load(match.group("yaml")) or {}
    if not isinstance(meta, dict):
        raise ValueError("Frontmatter did not parse to a mapping")
    return meta, match.group("body")


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value]
    return [str(value)]


def load_playbook(path: Path) -> Playbook:
    raw = path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)
    pb_id = str(meta.get("id") or path.stem)
    return Playbook(
        id=pb_id,
        path=path,
        title=str(meta.get("title", pb_id)),
        description=str(meta.get("description", "")),
        category=str(meta.get("category", "")),
        ticket_class=str(meta.get("ticket_class", "")),
        issue_category=str(meta.get("issue_category", "")),
        languages=[s.lower() for s in _as_str_list(meta.get("languages"))],
        country_focus=[s.lower() for s in _as_str_list(meta.get("country_focus"))],
        resolution_pattern=str(meta.get("resolution_pattern", "")),
        when_applies=extract_section(body, "When this applies"),
        resolution_flow=extract_section(body, "Typical resolution flow", "Resolution flow"),
        typical_actions=extract_section(body, "Typical actions"),
        risks=extract_section(body, "Safety constraints", "Risks"),
        body=body,
        raw=raw,
        metadata=meta,
    )


def discover_playbook_paths(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.md")
        if p.name not in _NON_PLAYBOOK_BASENAMES
    )


def _signature(paths: Sequence[Path]) -> str:
    """Hash of (relative_path, mtime, size) tuples so the cache invalidates
    whenever any indexed file changes."""
    hasher = hashlib.sha256()
    for p in paths:
        stat = p.stat()
        hasher.update(p.name.encode())
        hasher.update(str(stat.st_mtime_ns).encode())
        hasher.update(str(stat.st_size).encode())
    return hasher.hexdigest()


class PlaybookIndex:
    """In-memory index over playbooks with cached embeddings."""

    def __init__(
        self,
        playbooks: list[Playbook],
        embeddings: np.ndarray,
        provider_name: str,
    ) -> None:
        if len(playbooks) != embeddings.shape[0]:
            raise ValueError("playbooks/embeddings length mismatch")
        self.playbooks = playbooks
        self.embeddings = embeddings  # (N, dim), L2-normalized
        self.provider_name = provider_name
        self._by_id = {p.id: p for p in playbooks}

    def __len__(self) -> int:
        return len(self.playbooks)

    def get(self, playbook_id: str) -> Playbook | None:
        return self._by_id.get(playbook_id)

    def filtered_indices(
        self,
        country: str | None,
        language: str | None,
        ticket_class: str | None,
    ) -> np.ndarray:
        keep = np.ones(len(self.playbooks), dtype=bool)
        for i, pb in enumerate(self.playbooks):
            if ticket_class and pb.ticket_class and pb.ticket_class != ticket_class:
                keep[i] = False
                continue
            if country and pb.country_focus:
                if country not in pb.country_focus and "other" not in pb.country_focus:
                    keep[i] = False
                    continue
            if language and pb.languages:
                if language not in pb.languages and "other" not in pb.languages:
                    keep[i] = False
        return np.flatnonzero(keep)

    def search(
        self,
        query_vector: np.ndarray,
        *,
        country: str | None = None,
        language: str | None = None,
        ticket_class: str | None = None,
        top_k: int = config.TOP_K_RETRIEVAL,
        min_confidence: float = config.MIN_RETRIEVAL_CONFIDENCE,
    ) -> list[RetrievalHit]:
        candidates = self.filtered_indices(country, language, ticket_class)
        # Fallback: if filters wiped everything out, search the full index so
        # we always return *something* — the UI can warn on low confidence.
        if candidates.size == 0:
            candidates = np.arange(len(self.playbooks))
        sims = self.embeddings[candidates] @ query_vector
        order = np.argsort(-sims)[:top_k]
        hits: list[RetrievalHit] = []
        for rank, local_idx in enumerate(order):
            score = float(sims[local_idx])
            if score < min_confidence and rank > 0:
                break
            global_idx = int(candidates[local_idx])
            hits.append(
                RetrievalHit(
                    playbook=self.playbooks[global_idx],
                    score=score,
                    rank=rank,
                )
            )
        return hits


def _load_cache(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = np.load(path, allow_pickle=False)
        return {
            "signature": str(data["signature"]),
            "provider": str(data["provider"]),
            "ids": [str(x) for x in data["ids"].tolist()],
            "embeddings": data["embeddings"],
        }
    except Exception:
        return None


def _save_cache(path: Path, *, signature: str, provider: str, ids: list[str], embeddings: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        signature=np.array(signature),
        provider=np.array(provider),
        ids=np.array(ids),
        embeddings=embeddings,
    )


def build_index(
    *,
    playbooks_dir: Path = config.PLAYBOOKS_DIR,
    cache_path: Path = config.EMBEDDING_CACHE_PATH,
    provider: EmbeddingProvider | None = None,
) -> PlaybookIndex:
    provider = provider or get_embedding_provider()
    paths = discover_playbook_paths(playbooks_dir)
    if not paths:
        raise FileNotFoundError(f"No playbooks found under {playbooks_dir}")
    playbooks = [load_playbook(p) for p in paths]
    signature = _signature(paths)

    cache = _load_cache(cache_path)
    cache_hit = (
        cache is not None
        and cache["signature"] == signature
        and cache["provider"] == provider.name
        and cache["ids"] == [pb.id for pb in playbooks]
    )
    if cache_hit:
        assert cache is not None  # narrow for type-checker; cache_hit implies non-None
        embeddings = cache["embeddings"].astype(np.float32)
    else:
        embeddings = provider.embed_matrix([pb.search_text for pb in playbooks])
        _save_cache(
            cache_path,
            signature=signature,
            provider=provider.name,
            ids=[pb.id for pb in playbooks],
            embeddings=embeddings,
        )

    return PlaybookIndex(playbooks=playbooks, embeddings=embeddings, provider_name=provider.name)


def detect_language(text: str) -> str | None:
    """Best-effort ISO 639-1 language code. None on failure or empty input."""
    if not text or not text.strip():
        return None
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        return detect(text).lower()
    except Exception:
        return None


def country_from_labels(labels: Iterable[str]) -> str | None:
    """Map Jira label tokens like 'croatia' to ISO codes like 'hr'."""
    for label in labels:
        token = str(label).strip().lower()
        if token in _COUNTRY_TOKEN_TO_ISO:
            return _COUNTRY_TOKEN_TO_ISO[token]
    return None


def retrieve(
    index: PlaybookIndex,
    ticket_text: str,
    *,
    labels: Iterable[str] | None = None,
    ticket_class: str | None = None,
    top_k: int = config.TOP_K_RETRIEVAL,
    provider: EmbeddingProvider | None = None,
) -> list[RetrievalHit]:
    """End-to-end retrieval for one ticket: detect language + country, embed, search."""
    provider = provider or get_embedding_provider()
    query_vector = np.asarray(provider.embed(ticket_text), dtype=np.float32)
    return index.search(
        query_vector,
        country=country_from_labels(labels or []),
        language=detect_language(ticket_text),
        ticket_class=ticket_class,
        top_k=top_k,
    )
