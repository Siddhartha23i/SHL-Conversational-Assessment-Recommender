# SHL Assignment — Setup & Run Guide

## Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

> Takes ~5 min on first run (downloads sentence-transformers model ~80MB)

---

## Step 2 — Configure API Key

Create `.env` from the template:

```bash
copy .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_actual_key_here
```

Get a free key at: https://console.groq.com/keys

---

## Step 3 — Build the data pipeline

Run these **once** in order:

```bash
# 3a: Clean the catalog
python scripts/preprocess.py

# 3b: Build FAISS index (downloads model + encodes ~300 docs, takes 1-2 min)
python scripts/build_index.py
```

Expected output:
```
Loaded 300+ assessments.
Encoding 300+ documents with Sentence-BERT...
FAISS index built — 300+ vectors, dim=384
Saved index → data/faiss_index.bin
Quick search test:
  1. [0.8912] Core Java (New)
  2. [0.8734] Java 8 (New)
  ...
```

---

## Step 4 — Run the API

```powershell
# Windows (user-level install — uvicorn not on PATH)
python -m uvicorn api.main:app --reload --port 8000
```

Test it (in a new terminal):
```powershell
# Health check
Invoke-WebRequest http://localhost:8000/health

# Or use curl if installed:
curl http://localhost:8000/health

# Chat request
$body = '{"messages": [{"role": "user", "content": "I am hiring a Java developer"}]}'
Invoke-WebRequest -Uri http://localhost:8000/chat -Method POST `
  -ContentType "application/json" -Body $body
```

Swagger UI (interactive docs): http://localhost:8000/docs

Swagger docs: http://localhost:8000/docs

---

## Step 5 — Run the Streamlit UI

```bash
streamlit run ui/app.py
```

Opens at: http://localhost:8501

---

## Step 6 — Run Evaluation

```bash
python evaluation/evaluate.py
```

---

## Step 7 — Deploy

### API → Render.com
1. Push project to GitHub (run `git init`, `git add .`, `git commit`)
2. Go to render.com → New Web Service → Connect repo
3. Environment: Add `GROQ_API_KEY`
4. Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
5. **Important**: Add `data/` files to the repo OR use a build command to generate them

### UI → Streamlit Cloud  
1. Go to share.streamlit.io → Deploy → Connect repo
2. Main file: `ui/app.py`
3. Secrets: Add `GROQ_API_KEY`
4. Optionally: `RECOMMENDER_API_URL = https://your-render-app.onrender.com`

---

## File Structure Reference

```
SHL_Assignment/
├── shl_product_catalog.json      ← Raw catalog (already exists)
├── requirements.txt
├── .env                          ← Create from .env.example (never commit!)
├── Dockerfile
├── src/
│   ├── agent.py                  ← Main conversational agent (the brain)
│   ├── config.py                 ← All settings
│   ├── data_loader.py            ← Catalog loading + preprocessing
│   ├── embedder.py               ← Sentence-BERT + FAISS
│   └── models.py                 ← API schemas (non-negotiable)
├── api/main.py                   ← FastAPI: GET /health, POST /chat
├── ui/app.py                     ← Streamlit chat UI
├── scripts/
│   ├── preprocess.py             ← Run first
│   └── build_index.py            ← Run second
├── evaluation/
│   ├── test_conversations.json   ← 10 real sample traces
│   └── evaluate.py               ← Recall@10 scorer
└── data/                         ← Generated (gitignored)
    ├── cleaned_catalog.json
    ├── faiss_index.bin
    └── embeddings.npy
```
