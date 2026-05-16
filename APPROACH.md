# Approach Document
## SHL Conversational Assessment Recommender

**Siddhartha | May 2026**

---

### What I Built

I built a conversational system where a hiring manager can describe a role in plain English, and the system guides them through a short dialogue to produce a shortlist of up to 10 relevant SHL assessments. The system exposes a `/chat` API endpoint that accepts the full conversation history and returns a structured reply with assessment recommendations.

---

### Design Choices

The core idea was to split the problem into two steps: **find** and **choose**.

**Step 1 — Find (Retrieval):** Instead of searching the catalog by keywords, I used a sentence embedding model (`all-MiniLM-L6-v2` from Sentence Transformers) to convert both the user's query and each assessment description into vectors. I then used FAISS, a fast similarity search library, to find the top 24 most semantically similar assessments from the catalog. This works much better than keyword search because phrases like "team lead" and "people manager" are treated as similar even though they share no words.

**Step 2 — Choose (LLM reasoning):** Once I have 24 candidate assessments, I pass them along with the conversation history to an LLM — specifically LLaMA 3.3 70B running on Groq. The LLM reads the candidates and the context, then decides which 10 to pick and writes a short explanation. It also decides what to do next: ask a clarifying question, return a shortlist, refine an existing one, or decline if the request is off-topic.

I chose this two-step approach because sending all 370 catalog items to the LLM on every turn would be slow and expensive. The retrieval step acts as a smart pre-filter.

---

### Retrieval Setup

- **Model:** `all-MiniLM-L6-v2` — a small, fast model (22M parameters) that produces 384-dimensional vectors
- **Index type:** FAISS `IndexFlatIP` — exact inner-product search, which equals cosine similarity when vectors are normalized
- **Catalog size:** 370 individual SHL assessments (packaged Job Solutions excluded per the spec)
- **Retrieval count:** Top 24 candidates sent to the LLM, which selects the final 10

The embeddings and FAISS index are built once using `scripts/build_index.py` and saved to disk. On server startup, the API loads them from disk so there is no rebuild overhead at request time.

---

### Prompt Design

The LLM receives a system prompt that defines six possible actions it can take:

- **clarify** — ask one focused question when critical information is missing
- **recommend** — return a shortlist when enough context exists
- **refine** — update the shortlist based on new constraints
- **compare** — explain differences between assessments without returning a new list
- **confirm** — finalize when the user agrees with the current shortlist
- **refuse** — decline off-topic, legal, or prompt-injection attempts

The LLM always responds in JSON:
```json
{ "action": "recommend", "reply": "...", "selected_names": ["Assessment A", ...] }
```

This structured output means the backend always knows exactly what to do — it is not parsing free-form text. The selected names are cross-referenced against the real catalog to guarantee catalog-grounded URLs in the response.

One thing I added was a **hard guard in Python** before the LLM is called: if the user's message is very short and contains no job-related words (e.g., "hi" or "hello"), the system immediately asks for the role without invoking the LLM at all. This prevents unnecessary API calls and stops the LLM from hallucinating a shortlist for vague inputs.

---

### What Didn't Work

**Google Gemini (initial choice):** I originally used Google's GenAI SDK but kept hitting quota limits (429 errors) during testing. I switched to Groq, which has a generous free tier and is significantly faster (~200 tokens per second).

**Multi-line f-strings in Streamlit:** The UI was rendering HTML as raw code because Streamlit's markdown parser treats 4+ leading spaces as a code block. All HTML rendering had to be rewritten using single-line string concatenation.

**LLM recommending on "hi":** The LLM would sometimes return a shortlist even when the user just greeted it. This was fixed with the Python-level input guard described above.

---

### Evaluation Approach

I wrote a local evaluator (`evaluation/evaluate.py`) that replays conversation traces statelessly and computes **Recall@10** — what fraction of relevant assessments appear in the returned shortlist. The evaluator stops as soon as a shortlist is returned, mirrors the 8-message conversation cap, and sends requests to the live API rather than calling the agent directly.

The FAISS step is tuned to retrieve 24 candidates (more than needed) to maximize recall before the LLM does the final selection. This separation keeps the retrieval recall high while letting the LLM handle precision.

---

### AI Tools Used

I used an AI coding assistant (Antigravity / Gemini) extensively for:
- Generating the base FastAPI and Streamlit scaffolding
- Drafting and iterating on the system prompt
- Debugging Streamlit CSS rendering issues
- Writing this document's initial draft (then edited for clarity and tone)

All architectural decisions, model selections, and the core agent logic were reviewed and refined by me. The AI was used as an accelerator, not a replacement for understanding.

---

*Submitted as part of the SHL AI Internship Assessment — May 2026*
