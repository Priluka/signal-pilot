"""Embedding provider abstraction.

A thin interface so the rest of the codebase never imports a concrete model.
Two backends today: ``local`` (sentence-transformers, BGE-m3) and ``voyage``
(Voyage AI REST API). Flip ``EMBEDDING_PROVIDER`` in .env to swap; the
retrieval cache key embeds ``provider.name`` so changing providers
triggers a full re-embed on next index build.
"""
from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Sequence

import numpy as np

import config


class EmbeddingProvider(ABC):
    """Vector encoder. Implementations must return L2-normalized float32 vectors
    so downstream cosine similarity reduces to a dot product."""

    name: str
    dim: int

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        ...

    @abstractmethod
    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        ...

    def embed_matrix(self, texts: Sequence[str]) -> np.ndarray:
        """Convenience: return a (N, dim) float32 matrix for batch ops."""
        vectors = self.embed_batch(list(texts))
        return np.asarray(vectors, dtype=np.float32)


class LocalSentenceTransformerProvider(EmbeddingProvider):
    """sentence-transformers backend. Loads the model lazily on first use."""

    def __init__(self, model_name: str, device: str) -> None:
        self.name = f"local:{model_name}"
        self._model_name = model_name
        self._device = device
        self._model = None  # lazy
        self._dim: int | None = None

    def _ensure_loaded(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name, device=self._device)
            self._dim = int(self._model.get_sentence_embedding_dimension())
        return self._model

    @property
    def dim(self) -> int:  # type: ignore[override]
        self._ensure_loaded()
        assert self._dim is not None
        return self._dim

    def embed(self, text: str) -> list[float]:
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        model = self._ensure_loaded()
        vectors = model.encode(
            list(texts),
            batch_size=16,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.astype(np.float32).tolist()


class VoyageEmbeddingProvider(EmbeddingProvider):
    """Voyage AI REST backend.

    ``embed_batch`` is treated as the indexing path → ``input_type='document'``.
    ``embed`` is treated as the retrieval path → ``input_type='query'``.
    Voyage models return L2-normalized vectors out of the box, so we keep
    them as-is — same contract as the local provider.

    Network calls go through httpx (already a transitive dep of the
    anthropic SDK). The dim is set lazily after the first response, since
    Voyage doesn't expose a metadata endpoint and hardcoding it would
    break silently on a model swap.
    """

    _ENDPOINT = "https://api.voyageai.com/v1/embeddings"
    # Trial accounts cap at 3 RPM / 10K TPM. 16 playbooks per request keeps
    # each call comfortably under the TPM bound (~4–5K tokens) and we sleep
    # between batches so the RPM throttle doesn't trip. Paid tiers ignore
    # both bounds — the small batch is harmless overhead in that case.
    _BATCH_SIZE = 16
    _MIN_INTERBATCH_S = 22.0
    _TIMEOUT_S = 60.0

    def __init__(self, model_name: str, api_key: str) -> None:
        if not api_key:
            raise RuntimeError(
                "VOYAGE_API_KEY is not set. Add it to .env or your shell env."
            )
        self.name = f"voyage:{model_name}"
        self._model_name = model_name
        self._api_key = api_key
        self._dim: int | None = None

    @property
    def dim(self) -> int:  # type: ignore[override]
        if self._dim is None:
            # Force a one-token probe so dim is known before any caller asks.
            # Cheap (single short string, single API call) and only happens
            # the very first time anything touches the provider.
            self.embed_batch(["."])
        assert self._dim is not None
        return self._dim

    def embed(self, text: str) -> list[float]:
        return self._call([text], input_type="query")[0]

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        out: list[list[float]] = []
        batch: list[str] = list(texts)
        total = len(batch)
        for i in range(0, total, self._BATCH_SIZE):
            chunk = batch[i : i + self._BATCH_SIZE]
            out.extend(self._call(chunk, input_type="document"))
            # Pace under trial-account 3 RPM ceiling. Skipping the sleep
            # on the final chunk so paid accounts don't pay a tail penalty.
            if i + self._BATCH_SIZE < total:
                time.sleep(self._MIN_INTERBATCH_S)
        return out

    def _call(self, inputs: list[str], *, input_type: str) -> list[list[float]]:
        # Lazy-import httpx so the module still loads in environments where
        # only the local provider is wired up.
        import httpx

        payload = {
            "input": inputs,
            "model": self._model_name,
            "input_type": input_type,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        # Light retry loop for 429 / 5xx — Voyage's documented behavior is
        # to return Retry-After on rate limit; we honor it when present.
        # Trial accounts (3 RPM) need long-ish waits, so cap is 30s per
        # attempt and we burn up to 6 retries before giving up.
        attempts = 0
        while True:
            attempts += 1
            with httpx.Client(timeout=self._TIMEOUT_S) as client:
                resp = client.post(self._ENDPOINT, json=payload, headers=headers)
            if resp.status_code == 200:
                break
            if resp.status_code in (429, 500, 502, 503, 504) and attempts < 6:
                wait = float(resp.headers.get("Retry-After", "25"))
                time.sleep(min(wait, 30.0))
                continue
            raise RuntimeError(
                f"Voyage embed failed: {resp.status_code} {resp.text[:200]}"
            )

        data = resp.json()
        # Voyage's response order is preserved but each entry carries
        # ``index`` — sort by it to be safe across SDK/HTTP versions.
        rows = sorted(data["data"], key=lambda d: d["index"])
        vectors = [list(map(float, r["embedding"])) for r in rows]
        if self._dim is None and vectors:
            self._dim = len(vectors[0])
        return vectors


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """Factory dispatch. Adding a new backend means one elif branch here."""
    provider = config.EMBEDDING_PROVIDER.lower()
    if provider == "local":
        return LocalSentenceTransformerProvider(
            model_name=config.EMBEDDING_MODEL_LOCAL,
            device=config.EMBEDDING_DEVICE,
        )
    if provider == "voyage":
        return VoyageEmbeddingProvider(
            model_name=config.EMBEDDING_MODEL_VOYAGE,
            api_key=os.environ.get("VOYAGE_API_KEY", ""),
        )
    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {config.EMBEDDING_PROVIDER!r}")
