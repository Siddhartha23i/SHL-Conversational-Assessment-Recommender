"""
scripts/build_index.py — One-time script: embed all documents and build FAISS index.

Run from project root AFTER running preprocess.py:
    python scripts/build_index.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_cleaned_catalog
from src.embedder import Embedder
from src.config import CLEANED_CATALOG_PATH, FAISS_INDEX_PATH, EMBEDDINGS_PATH


def main() -> None:
    print(f"Loading cleaned catalog from: {CLEANED_CATALOG_PATH}")
    catalog = load_cleaned_catalog()
    print(f"Loaded {len(catalog)} assessments.")

    documents = [item["document"] for item in catalog]
    print(f"Encoding {len(documents)} documents with Sentence-BERT …")

    embedder = Embedder()
    embeddings = embedder.encode(documents)
    print(f"Encoding complete. Shape: {embeddings.shape}")

    embedder.build_index(embeddings)
    embedder.save(FAISS_INDEX_PATH, EMBEDDINGS_PATH)

    # Quick search test
    print("\n── Quick search test ─────────────────────────────────────────")
    test_query = "Java developer backend architecture"
    hits = embedder.search(test_query, top_k=3)
    for rank, (idx, score) in enumerate(hits, 1):
        print(f"  {rank}. [{score:.4f}] {catalog[idx]['name']}")
    print("─────────────────────────────────────────────────────────────")
    print("\nIndex build complete.")


if __name__ == "__main__":
    main()
