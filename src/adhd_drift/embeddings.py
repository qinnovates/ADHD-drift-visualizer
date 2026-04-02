"""Embedding providers for semantic distance computation.

Supports multiple backends:
- voyage: Voyage AI embeddings (default if VOYAGE_API_KEY set)
- openai: OpenAI API embeddings (default if OPENAI_API_KEY set)
- local: MiniLM via sentence-transformers (offline fallback, no API needed)

The provider is auto-detected from environment variables.
Override with ADHD_DRIFT_EMBEDDINGS=voyage|openai|local.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

import numpy as np

_provider = None


class EmbeddingProvider(ABC):
    """Interface for embedding backends."""

    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        """Embed a single text string. Returns normalized vector."""

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts. Returns matrix of normalized vectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name for logging."""


class VoyageEmbeddings(EmbeddingProvider):
    """Voyage AI embeddings (recommended with Anthropic stack).

    Requires VOYAGE_API_KEY or ANTHROPIC_API_KEY env var.
    Uses voyageai package: pip install voyageai
    """

    def __init__(self) -> None:
        import voyageai

        self._client = voyageai.Client()

    @property
    def name(self) -> str:
        return "voyage"

    def embed(self, text: str) -> np.ndarray:
        result = self._client.embed([text], model="voyage-3")
        vec = np.array(result.embeddings[0], dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        result = self._client.embed(texts, model="voyage-3")
        vecs = np.array(result.embeddings, dtype=np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms


class OpenAIEmbeddings(EmbeddingProvider):
    """OpenAI API embeddings."""

    def __init__(self) -> None:
        import openai

        self._client = openai.OpenAI()

    @property
    def name(self) -> str:
        return "openai"

    def embed(self, text: str) -> np.ndarray:
        response = self._client.embeddings.create(
            model="text-embedding-3-small",
            input=[text],
        )
        vec = np.array(response.data[0].embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        response = self._client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        vecs = np.array([d.embedding for d in response.data], dtype=np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms


class LocalEmbeddings(EmbeddingProvider):
    """Offline embeddings via sentence-transformers MiniLM."""

    def __init__(self) -> None:
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    @property
    def name(self) -> str:
        return "local"

    def embed(self, text: str) -> np.ndarray:
        model = self._get_model()
        vec = model.encode(text, normalize_embeddings=True)
        return np.array(vec)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        model = self._get_model()
        vecs = model.encode(texts, normalize_embeddings=True)
        return np.array(vecs)


def _detect_provider() -> EmbeddingProvider:
    """Auto-detect the best available embedding provider."""
    override = os.environ.get("ADHD_DRIFT_EMBEDDINGS", "").lower()

    if override == "voyage":
        return VoyageEmbeddings()
    elif override == "openai":
        return OpenAIEmbeddings()
    elif override == "local":
        return LocalEmbeddings()

    if os.environ.get("VOYAGE_API_KEY"):
        return VoyageEmbeddings()
    if os.environ.get("OPENAI_API_KEY"):
        return OpenAIEmbeddings()

    return LocalEmbeddings()


def get_provider() -> EmbeddingProvider:
    """Get or create the embedding provider singleton."""
    global _provider
    if _provider is None:
        _provider = _detect_provider()
    return _provider


def set_provider(provider: EmbeddingProvider) -> None:
    """Override the embedding provider (useful for testing)."""
    global _provider
    _provider = provider


def embed(text: str) -> np.ndarray:
    """Embed a single text string. Returns normalized vector."""
    return get_provider().embed(text)


def embed_batch(texts: list[str]) -> np.ndarray:
    """Embed multiple texts. Returns matrix of normalized vectors."""
    return get_provider().embed_batch(texts)


def cosine_distance(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Cosine distance between two normalized vectors. Range [0, 1]."""
    similarity = float(np.dot(vec_a, vec_b))
    return max(0.0, 1.0 - similarity)


def semantic_distance(text_a: str, text_b: str) -> float:
    """End-to-end semantic distance between two texts. Range [0, 1]."""
    vec_a = embed(text_a)
    vec_b = embed(text_b)
    return cosine_distance(vec_a, vec_b)
