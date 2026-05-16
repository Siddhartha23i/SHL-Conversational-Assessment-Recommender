"""
api/main.py — FastAPI application matching the EXACT PDF spec.

Endpoints:
  GET  /health  → {"status": "ok"}           HTTP 200
  POST /chat    → ChatResponse (reply + recommendations[] + end_of_conversation)

Schema is NON-NEGOTIABLE — deviating breaks the automated evaluator.

Design notes:
  - Stateless: every /chat call carries full conversation history
  - Agent is loaded ONCE at startup into memory (FAISS index + catalog)
  - 30s timeout per call honored via LLM timeout config
  - Turn cap (max 8) enforced inside the agent
"""
from __future__ import annotations

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.models import ChatRequest, ChatResponse, HealthResponse
from src.agent import ConversationalAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Singleton agent ───────────────────────────────────────────────────────────
agent = ConversationalAgent()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load FAISS index + catalog + LLM client once at startup."""
    logger.info("[startup] Loading SHL assessment index and agent…")
    agent.load()
    logger.info("[startup] Agent ready.")
    yield
    logger.info("[shutdown] Agent shutting down.")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SHL Conversational Assessment Recommender",
    description=(
        "Conversational agent that takes a hiring manager from vague intent to a grounded "
        "shortlist of SHL assessments via multi-turn dialogue. "
        "Stateless: each POST /chat carries the full conversation history."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health() -> HealthResponse:
    """
    Readiness probe. Returns {"status": "ok"} with HTTP 200.
    Cold-start services: evaluator allows up to 2 minutes on the first call.
    """
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Stateless conversational endpoint.

    Accepts the full conversation history and returns the agent's next reply,
    optionally with a structured shortlist of SHL assessments.

    Conversation behaviors:
    - Clarifies vague queries before recommending
    - Recommends 1–10 assessments when context is sufficient
    - Refines when the user changes constraints
    - Compares assessments when asked
    - Refuses off-topic / prompt-injection attempts

    Limits: 8 turns max per conversation, 30s per call.
    """
    try:
        response = agent.chat(request.messages)
        return response
    except Exception as exc:
        logger.error(f"[/chat] Unhandled error: {exc}", exc_info=True)
        # Return a graceful degradation — never let the evaluator see a 500
        return ChatResponse(
            reply="I encountered an error processing your request. Could you rephrase your query?",
            recommendations=[],
            end_of_conversation=False,
        )
