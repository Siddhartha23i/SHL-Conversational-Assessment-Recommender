"""
src/recommender.py — Legacy single-shot retrieval helper.

This module is retained as a utility for scripts and evaluation.
The main conversational pipeline lives in src/agent.py.
"""
from __future__ import annotations
import logging
from src.embedder import Embedder
from src.data_loader import load_cleaned_catalog
from src.config import FAISS_TOP_K, FINAL_TOP_K

logger = logging.getLogger(__name__)


class Retriever:
    """Simple FAISS-based retrieval without conversational logic. Used by scripts."""

    def __init__(self) -> None:
        self.catalog: list[dict] = []
        self.embedder = Embedder()
        self._loaded = False

    def load(self) -> None:
        self.catalog = load_cleaned_catalog()
        self.embedder.load()
        self._loaded = True
        logger.info(f"[retriever] Loaded {len(self.catalog)} assessments.")

    def search(self, query: str, top_k: int = FINAL_TOP_K) -> list[dict]:
        """Return top-k catalog items for a query string."""
        hits = self.embedder.search(query, top_k=min(top_k, FAISS_TOP_K))
        results = []
        for idx, score in hits:
            if 0 <= idx < len(self.catalog):
                item = dict(self.catalog[idx])
                item["_score"] = score
                results.append(item)
        return results[:top_k]
