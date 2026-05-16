"""
models.py — Pydantic v2 schemas matching the EXACT PDF-specified API contract.

WARNING: The schema is non-negotiable. Deviating breaks the automated evaluator.

POST /chat
  Request:  { "messages": [{"role": str, "content": str}, ...] }
  Response: { "reply": str, "recommendations": [...], "end_of_conversation": bool }

GET /health
  Response: { "status": "ok" }
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


# ── Test-type short codes ──────────────────────────────────────────────────────
# Mapped from SHL catalog "keys" field values
TEST_TYPE_MAP: dict[str, str] = {
    "Knowledge & Skills": "K",
    "Personality & Behavior": "P",
    "Ability & Aptitude": "A",
    "Competencies": "C",
    "Simulations": "S",
    "Assessment Exercises": "E",
    "Development & 360": "D",
    "Biodata & Situational Judgment": "B",
}


def keys_to_type_code(keys: list[str]) -> str:
    """Return the primary test-type short code for a list of SHL catalog keys."""
    for key in keys:
        if key in TEST_TYPE_MAP:
            return TEST_TYPE_MAP[key]
    return "K"  # default fallback


# ── Chat endpoint schemas ──────────────────────────────────────────────────────

class Message(BaseModel):
    """A single turn in the conversation history."""
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """POST /chat — request body. Full conversation history, stateless."""
    messages: list[Message] = Field(
        ...,
        min_length=1,
        description="Full conversation history including the latest user message.",
    )


class RecommendationItem(BaseModel):
    """A single assessment in the shortlist. Schema is non-negotiable."""
    name: str = Field(description="Assessment name as it appears in the SHL catalog.")
    url: str = Field(description="Canonical SHL catalog URL for this assessment.")
    test_type: str = Field(
        description="Single-letter type code: K=Knowledge, P=Personality, A=Ability, C=Competencies, S=Simulations, E=Exercises, D=Development, B=Biodata."
    )


class ChatResponse(BaseModel):
    """POST /chat — response body. Schema is non-negotiable per PDF spec."""
    reply: str = Field(description="The agent's natural-language reply.")
    recommendations: list[RecommendationItem] = Field(
        default_factory=list,
        description="Empty while gathering context. 1–10 items when agent commits to a shortlist.",
    )
    end_of_conversation: bool = Field(
        default=False,
        description="True only when the agent considers the task complete.",
    )


# ── Health check schema ───────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """GET /health — must return exactly this."""
    status: str = "ok"
