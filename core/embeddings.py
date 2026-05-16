"""Embedding provider abstraction.

A thin interface so the rest of the codebase never imports a concrete model.
Today: local sentence-transformers (BGE-m3). Tomorrow: Voyage AI — implement
`VoyageEmbeddingProvider` below and flip `EMBEDDING_PROVIDER` in config.
"""
from __future__ import annotations

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
        raise NotImplementedError(
            "Voyage provider not implemented yet. Add VoyageEmbeddingProvider here "
            "and set ANTHROPIC/Voyage credentials in config."
        )
    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {config.EMBEDDING_PROVIDER!r}")
