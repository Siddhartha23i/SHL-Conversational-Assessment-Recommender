"""
evaluation/evaluate.py — Compute Recall@10 using the 10 real sample conversations.

Simulates multi-turn conversations locally against the agent.
Matches the PDF evaluator's methodology: stateless /chat replay.

Run from project root:
    python evaluation/evaluate.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent import ConversationalAgent
from src.config import MAX_CHAT_MESSAGES
from src.models import Message


def recall_at_k(recommended: list[str], relevant: list[str], k: int = 10) -> float:
    """Recall@K = |relevant ∩ top-K recommended| / |relevant|"""
    if not relevant:
        return 0.0
    top_k_set = set(recommended[:k])
    hits = sum(1 for name in relevant if name in top_k_set)
    return hits / len(relevant)


def simulate(agent: ConversationalAgent, user_turns: list[str]) -> list[str]:
    """
    Simulate a real multi-turn conversation.
    Returns the final list of recommended assessment names.
    """
    messages: list[Message] = []
    last_recs: list[str] = []

    for user_text in user_turns:
        if len(messages) >= MAX_CHAT_MESSAGES - 1:
            break

        messages.append(Message(role="user", content=user_text))
        response = agent.chat(messages)
        messages.append(Message(role="assistant", content=response.reply))

        if response.recommendations:
            last_recs = [r.name for r in response.recommendations]
            break

        if response.end_of_conversation:
            break

        if len(messages) >= MAX_CHAT_MESSAGES:
            break

    return last_recs


def main() -> None:
    traces_path = Path(__file__).parent / "test_conversations.json"
    with open(traces_path, encoding="utf-8") as f:
        traces = json.load(f)

    print("=" * 60)
    print("  SHL Assessment Recommender — Recall@10 Evaluation")
    print("=" * 60)
    print("\nLoading agent (this may take ~30s on first run)…")
    agent = ConversationalAgent()
    agent.load()
    print(f"Agent ready. Evaluating {len(traces)} conversation traces.\n")

    scores = []
    for trace in traces:
        trace_id = trace["id"]
        expected = trace["expected_assessments"]
        user_turns = trace["turns"]

        print(f"▶ {trace_id}")
        print(f"  Turns: {len(user_turns)} | Expected: {len(expected)} assessments")

        try:
            recommended = simulate(agent, user_turns)
        except Exception as e:
            print(f"  ERROR: {e}")
            recommended = []

        r10 = recall_at_k(recommended, expected, k=10)
        scores.append(r10)

        # Show hits and misses
        hits = [n for n in expected if n in recommended[:10]]
        misses = [n for n in expected if n not in recommended[:10]]
        print(f"  Recommended ({len(recommended)}): {recommended[:5]}{'…' if len(recommended)>5 else ''}")
        print(f"  Hits: {hits}")
        if misses:
            print(f"  Missed: {misses}")
        bar = "█" * int(r10 * 20) + "░" * (20 - int(r10 * 20))
        print(f"  Recall@10: {r10:.3f}  [{bar}]\n")

    mean_r10 = sum(scores) / len(scores) if scores else 0.0
    print("=" * 60)
    print(f"  Mean Recall@10: {mean_r10:.4f}  ({mean_r10*100:.1f}%)")
    print("=" * 60)
    print("\nPer-trace summary:")
    for trace, score in zip(traces, scores):
        mark = "✓" if score >= 0.5 else "✗"
        print(f"  {mark} {trace['id']:<40} {score:.3f}")


if __name__ == "__main__":
    main()
