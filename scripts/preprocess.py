"""
scripts/preprocess.py — Phase 0: Load raw catalog, clean, and save to data/cleaned_catalog.json

Run from project root:
    python scripts/preprocess.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import load_raw_catalog, preprocess_catalog, save_cleaned_catalog
from src.config import RAW_CATALOG_PATH, CLEANED_CATALOG_PATH


def main() -> None:
    print(f"Loading raw catalog: {RAW_CATALOG_PATH}")
    raw = load_raw_catalog()
    print(f"Loaded {len(raw)} valid assessments (status='ok').")

    cleaned = preprocess_catalog(raw)
    print(f"Preprocessed {len(cleaned)} assessments.")

    # Sanity check
    sample = cleaned[0]
    print("\n── Sample ────────────────────────────────────────────")
    print(f"  Name:     {sample['name']}")
    print(f"  Duration: {sample.get('duration_minutes')} min")
    print(f"  Document: {sample['document'][:200]}…")
    print("──────────────────────────────────────────────────────\n")

    save_cleaned_catalog(cleaned)
    print(f"✓ Saved → {CLEANED_CATALOG_PATH}")


if __name__ == "__main__":
    main()
