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
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

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
