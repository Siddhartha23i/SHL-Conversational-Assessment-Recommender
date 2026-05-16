"""
Configuration module — loads environment variables and defines constants.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

RAW_CATALOG_PATH = ROOT_DIR / "shl_product_catalog.json"
CLEANED_CATALOG_PATH = DATA_DIR / "cleaned_catalog.json"
FAISS_INDEX_PATH = DATA_DIR / "faiss_index.bin"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"

# ── Environment ───────────────────────────────────────────────────────────────
load_dotenv(ROOT_DIR / ".env")

def _get_groq_key() -> str:
    """Read GROQ_API_KEY from env, .env file, or Streamlit secrets (Cloud deployment)."""
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
    return key

GROQ_API_KEY: str = _get_groq_key()


# ── Model settings ────────────────────────────────────────────────────────────
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
EMBEDDING_DIM: int = 384

# ── Retrieval settings ────────────────────────────────────────────────────────
FAISS_TOP_K: int = 24          # candidates retrieved before re-ranking
FINAL_TOP_K: int = 10          # assessments returned to the caller
MAX_CHAT_MESSAGES: int = 8     # evaluator cap: user + assistant turns combined

# ── LLM settings ─────────────────────────────────────────────────────────────
# llama-3.3-70b-versatile: Groq's best model — 128k context, strong JSON
# instruction-following, 14,400 free requests/day, ~200 tok/s
GROQ_MODEL: str = "llama-3.3-70b-versatile"
LLM_TIMEOUT: int = 20          # seconds
LLM_MAX_RETRIES: int = 2
