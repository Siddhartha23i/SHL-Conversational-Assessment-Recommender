"""
embedder.py — Sentence-BERT encoding + FAISS index management.

Responsibilities:
  • Load the sentence-transformers model (all-MiniLM-L6-v2)
  • Encode a list of document strings → normalised numpy embeddings
  • Build a FAISS IndexFlatIP (cosine similarity via inner-product on unit vectors)
  • Persist / load index + metadata
  • search(query, top_k) → list of (index, score) tuples
"""
from __future__ import annotations

import numpy as np
import faiss
from pathlib import Path
from sentence_transformers import SentenceTransformer

from src.config import (
    EMBEDDING_MODEL_NAME,
    FAISS_INDEX_PATH,
    EMBEDDINGS_PATH,
    FAISS_TOP_K,
)


class Embedder:
    """Wraps the sentence-transformer model and FAISS index."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        print(f"[embedder] Loading model '{model_name}' …")
        self.model = SentenceTransformer(model_name)
        self.index: faiss.Index | None = None
        self._embeddings: np.ndarray | None = None

    # ── Encoding ──────────────────────────────────────────────────────────────

    def encode(self, texts: list[str], batch_size: int = 64) -> np.ndarray:
        """
        Encode texts into L2-normalised float32 embeddings.
        Normalisation turns inner-product into cosine similarity.
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.astype(np.float32)

    # ── Index management ──────────────────────────────────────────────────────

    def build_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Build a FAISS flat inner-product index from pre-encoded embeddings."""
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)
        index.add(embeddings)
        self.index = index
        self._embeddings = embeddings
        print(f"[embedder] FAISS index built — {index.ntotal} vectors, dim={dim}")
        return index

    def save(
        self,
        index_path: Path = FAISS_INDEX_PATH,
        embeddings_path: Path = EMBEDDINGS_PATH,
    ) -> None:
        """Persist index and raw embeddings to disk."""
        if self.index is None or self._embeddings is None:
            raise RuntimeError("No index to save. Call build_index() first.")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(index_path))
        np.save(str(embeddings_path), self._embeddings)
        print(f"[embedder] Saved index → {index_path}")
        print(f"[embedder] Saved embeddings → {embeddings_path}")

    def load(
        self,
        index_path: Path = FAISS_INDEX_PATH,
        embeddings_path: Path = EMBEDDINGS_PATH,
    ) -> None:
        """Load a pre-built FAISS index from disk (called on API startup)."""
        self.index = faiss.read_index(str(index_path))
        self._embeddings = np.load(str(embeddings_path))
        print(f"[embedder] Loaded index — {self.index.ntotal} vectors")

    # ── Search ────────────────────────────────────────────────────────────────

    def search(
        self, query: str, top_k: int = FAISS_TOP_K
    ) -> list[tuple[int, float]]:
        """
        Encode query and retrieve top-k most similar assessments.

        Returns:
            List of (catalog_index, cosine_score) sorted by score descending.
        """
        if self.index is None:
            raise RuntimeError("Index not loaded. Call load() or build_index() first.")

        query_vec = self.encode([query])           # shape (1, dim)
        scores, indices = self.index.search(query_vec, top_k)

        results = [
            (int(idx), float(score))
            for idx, score in zip(indices[0], scores[0])
            if idx >= 0
        ]
        return results
