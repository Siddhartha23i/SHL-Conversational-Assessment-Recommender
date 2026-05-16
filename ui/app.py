from __future__ import annotations

import html
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st

from src.config import FINAL_TOP_K, MAX_CHAT_MESSAGES

TYPE_LABELS = {
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "A": "Ability & Aptitude",
    "C": "Competencies",
    "S": "Simulations",
    "E": "Assessment Exercises",
    "D": "Development & 360",
    "B": "Biodata & Situational Judgment",
}

API_URL = os.getenv("RECOMMENDER_API_URL", "").rstrip("/")

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Cormorant+Garamond:wght@600;700&display=swap');

    /* ── Force light mode always, override system/browser dark mode ── */
    :root {
        color-scheme: light only;
        --bg: #f5efe4;
        --bg-soft: #fbf8f2;
        --panel: rgba(255, 252, 247, 0.86);
        --panel-strong: rgba(255, 255, 255, 0.92);
        --ink: #241d17;
        --muted: #6d6357;
        --line: rgba(92, 74, 38, 0.14);
        --gold: #b7872e;
        --gold-deep: #8a6218;
        --shadow: 0 24px 60px rgba(56, 42, 22, 0.08);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            color-scheme: light only;
            --bg: #f5efe4;
            --bg-soft: #fbf8f2;
            --panel: rgba(255, 252, 247, 0.86);
            --panel-strong: rgba(255, 255, 255, 0.92);
            --ink: #241d17;
            --muted: #6d6357;
            --line: rgba(92, 74, 38, 0.14);
            --gold: #b7872e;
            --gold-deep: #8a6218;
            --shadow: 0 24px 60px rgba(56, 42, 22, 0.08);
        }
    }

    html, body, [class*="css"] {
        font-family: 'Manrope', sans-serif;
        color: var(--ink) !important;
        background-color: #f5efe4 !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer {
        visibility: hidden;
    }

    /* Force the whole app light */
    html, body {
        color-scheme: light only !important;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(183, 135, 46, 0.12), transparent 28%),
            radial-gradient(circle at top right, rgba(142, 117, 75, 0.12), transparent 24%),
            linear-gradient(180deg, #f7f1e8 0%, #f4ede2 48%, #efe6d8 100%) !important;
    }

    /* Kill black header & footer toolbars Streamlit adds */
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    header[data-testid="stHeader"] {
        background: linear-gradient(180deg, #f7f1e8 0%, transparent 100%) !important;
        border-bottom: none !important;
        box-shadow: none !important;
    }

    /* Bottom bar — elevated warm card feel */
    [data-testid="stBottom"],
    [data-testid="stChatInputContainer"],
    .stChatInputContainer,
    [data-testid="stBottomBlockContainer"] {
        background: rgba(245, 239, 228, 0.97) !important;
        border-top: 1px solid rgba(92, 74, 38, 0.1) !important;
        box-shadow: 0 -8px 32px rgba(56, 42, 22, 0.07) !important;
        backdrop-filter: blur(12px) !important;
        padding: 0.75rem 1.25rem 1rem !important;
    }

    /* ── Chat input: ONE clean gold pill, no double border, no blue ── */

    /* Outer wrapper only gets the visible border */
    [data-testid="stChatInput"] {
        background: rgba(255, 253, 248, 0.98) !important;
        border: 1.5px solid rgba(183, 135, 46, 0.28) !important;
        border-radius: 28px !important;
        box-shadow: 0 4px 20px rgba(138, 98, 24, 0.09), 0 1px 4px rgba(56, 42, 22, 0.05) !important;
        transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
        outline: none !important;
        overflow: hidden !important;
    }

    /* ALL inner children: no border, no background, no outline */
    [data-testid="stChatInput"] *,
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] > div > div,
    [data-testid="stChatInput"] > div > div > div {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background: transparent !important;
    }

    /* Gold glow on focus — outer wrapper only */
    [data-testid="stChatInput"]:focus-within {
        border-color: rgba(183, 135, 46, 0.6) !important;
        box-shadow: 0 4px 24px rgba(138, 98, 24, 0.14), 0 0 0 3px rgba(183, 135, 46, 0.1) !important;
    }

    /* Textarea text and caret */
    [data-testid="stChatInput"] textarea {
        color: #241d17 !important;
        caret-color: #8a6218 !important;
        font-size: 0.95rem !important;
        font-family: 'Manrope', sans-serif !important;
        padding: 0.65rem 0.5rem !important;
        line-height: 1.6 !important;
        resize: none !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #b0a090 !important;
        opacity: 1 !important;
        font-style: italic !important;
    }

    /* Send button — circular gold */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #c49535, #8a6218) !important;
        color: #ffffff !important;
        border-radius: 50% !important;
        border: none !important;
        width: 2.4rem !important;
        height: 2.4rem !important;
        box-shadow: 0 4px 12px rgba(138, 98, 24, 0.35) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        margin: 0.2rem !important;
        flex-shrink: 0 !important;
    }

    [data-testid="stChatInput"] button:hover {
        transform: scale(1.08) !important;
        box-shadow: 0 6px 18px rgba(138, 98, 24, 0.45) !important;
    }


    /* Main content area — ensure enough bottom padding so spinners
       never overlap the sticky chat bar */
    [data-testid="stAppViewContainer"] > .main .block-container {
        padding-bottom: 12rem !important;
    }

    /* Spinner styling — give it card-like warmth and breathing room */
    [data-testid="stSpinner"],
    .stSpinner {
        background: rgba(255, 252, 247, 0.9) !important;
        border: 1px solid rgba(92, 74, 38, 0.14) !important;
        border-radius: 16px !important;
        padding: 0.9rem 1.2rem !important;
        margin: 1rem 0 1.5rem !important;
        color: #8a6218 !important;
        box-shadow: 0 8px 24px rgba(56, 42, 22, 0.07) !important;
    }

    [data-testid="stSpinner"] p,
    .stSpinner p,
    [data-testid="stSpinner"] span,
    .stSpinner span {
        color: #8a6218 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        max-width: 1180px;
        padding-top: 1.4rem;
    }

    /* Sidebar — warm cream, no dark bleed */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"] {
        background: #faf6ef !important;
        border-right: 1px solid rgba(92, 74, 38, 0.14) !important;
        color: #241d17 !important;
    }

    /* Sidebar text elements */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {
        color: #241d17 !important;
    }

    /* Sidebar caption / muted text */
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] small {
        color: #6d6357 !important;
    }

    /* Sidebar section dividers */
    section[data-testid="stSidebar"] hr {
        border-color: rgba(92, 74, 38, 0.14) !important;
    }

    .shell-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 26px;
        box-shadow: var(--shadow);
        backdrop-filter: blur(14px);
    }

    .hero {
        padding: 1.6rem 1.8rem 1.3rem;
        margin-bottom: 1rem;
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        border: 1px solid rgba(183, 135, 46, 0.26);
        border-radius: 999px;
        background: rgba(183, 135, 46, 0.09);
        color: var(--gold-deep);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 0.35rem 0.75rem;
    }

    .hero h1 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3.2rem;
        line-height: 0.95;
        margin: 0.85rem 0 0.4rem;
        color: var(--ink);
    }

    .hero p {
        max-width: 62ch;
        margin: 0;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.7;
    }

    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1rem;
    }

    .pill {
        background: rgba(255, 255, 255, 0.74);
        border: 1px solid var(--line);
        border-radius: 999px;
        color: var(--ink);
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0.45rem 0.8rem;
    }

    .metric-card {
        padding: 1rem 1.1rem;
        min-height: 122px;
    }

    .metric-label {
        color: var(--gold-deep);
        font-size: 0.73rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .metric-value {
        margin-top: 0.45rem;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--ink);
    }

    .metric-copy {
        margin-top: 0.3rem;
        color: var(--muted);
        font-size: 0.86rem;
        line-height: 1.6;
    }

    .status-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding: 0.95rem 1.1rem;
        margin: 1rem 0;
        background: rgba(255, 255, 255, 0.66);
        border: 1px solid var(--line);
        border-radius: 20px;
    }

    .status-title {
        font-weight: 700;
        color: var(--ink);
        font-size: 0.94rem;
    }

    .status-copy {
        color: var(--muted);
        font-size: 0.84rem;
        margin-top: 0.12rem;
    }

    .status-chip {
        border-radius: 999px;
        padding: 0.4rem 0.75rem;
        background: rgba(183, 135, 46, 0.1);
        border: 1px solid rgba(183, 135, 46, 0.24);
        color: var(--gold-deep);
        font-size: 0.78rem;
        font-weight: 700;
        white-space: nowrap;
    }

    .transcript {
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    .message {
        max-width: 84%;
        padding: 0.95rem 1.05rem;
        border-radius: 18px;
        margin: 0.65rem 0;
        line-height: 1.65;
        border: 1px solid var(--line);
        box-shadow: 0 10px 30px rgba(56, 42, 22, 0.05);
        color: #241d17 !important;
        font-size: 0.95rem !important;
    }

    .message-user {
        margin-left: auto;
        background: linear-gradient(135deg, rgba(183, 135, 46, 0.12), rgba(183, 135, 46, 0.05));
        color: #241d17 !important;
    }

    .message-assistant {
        background: rgba(255, 255, 255, 0.82);
        color: #241d17 !important;
    }

    .message-role {
        display: block;
        margin-bottom: 0.3rem;
        color: var(--gold-deep) !important;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .results-wrap {
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    .results-head {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .results-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1rem;
    }

    .results-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2rem;
        line-height: 1;
        margin: 0;
        color: var(--ink);
    }

    .results-copy {
        margin-top: 0.25rem;
        color: var(--muted);
        font-size: 0.88rem;
    }

    .result-card {
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(251, 247, 239, 0.9));
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        min-height: 174px;
        position: relative;
        overflow: hidden;
    }

    .result-rank {
        width: 2rem;
        height: 2rem;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        background: rgba(183, 135, 46, 0.12);
        color: var(--gold-deep);
        font-weight: 800;
        font-size: 0.82rem;
        border: 1px solid rgba(183, 135, 46, 0.2);
    }

    .result-name {
        margin-top: 0.8rem;
        font-size: 1rem;
        font-weight: 800;
        line-height: 1.4;
    }

    .result-name a {
        color: var(--ink);
        text-decoration: none;
    }

    .result-name a:hover {
        color: var(--gold-deep);
    }

    .result-types {
        margin-top: 0.45rem;
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.55;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin-top: 0.8rem;
    }

    .type-badge {
        border-radius: 999px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.84);
        color: var(--ink);
        padding: 0.28rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .empty-state {
        text-align: center;
        padding: 2.4rem 1.8rem;
        color: var(--muted);
    }

    .empty-state h3 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2rem;
        margin: 0 0 0.5rem;
        color: var(--ink);
    }

    .empty-state p {
        margin: 0 auto;
        max-width: 52ch;
        line-height: 1.75;
    }

    .sidebar-note {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.65;
    }

    .stButton > button {
        border-radius: 14px !important;
        border: 1px solid rgba(138, 98, 24, 0.18) !important;
        background: linear-gradient(135deg, #b7872e, #8a6218) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 12px 28px rgba(138, 98, 24, 0.18);
    }

    .stButton > button p,
    .stButton > button span,
    .stButton > button div {
        color: #ffffff !important;
    }

    .stButton > button:hover {
        border-color: rgba(138, 98, 24, 0.28) !important;
        color: #ffffff !important;
    }

    @media (max-width: 900px) {
        .hero h1 {
            font-size: 2.5rem;
        }

        .message {
            max-width: 100%;
        }

        .results-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_agent():
    from src.agent import ConversationalAgent

    agent = ConversationalAgent()
    agent.load()
    return agent


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.recommendations = []
    st.session_state.show_recommendations = False
    st.session_state.ended = False
    st.session_state.error_message = ""
    st.session_state.pending_prompt = ""


def call_chat(messages: list[dict]) -> dict:
    if API_URL:
        import requests

        response = requests.post(
            f"{API_URL}/chat",
            json={"messages": messages},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    from src.models import Message

    agent = get_agent()
    payload = [Message(role=message["role"], content=message["content"]) for message in messages]
    return agent.chat(payload).model_dump()


def render_result_card(rank: int, rec: dict) -> str:
    name = html.escape(rec.get("name", ""))
    url = html.escape(rec.get("url", "#"))
    raw_types = rec.get("test_type", "K")
    codes = [code.strip() for code in raw_types.split(",") if code.strip()]
    type_names = " + ".join(TYPE_LABELS.get(code, code) for code in codes) or "Assessment"
    badges = "".join(
        f"<span class='type-badge' title='{html.escape(TYPE_LABELS.get(code, code))}'>{html.escape(code)}</span>"
        for code in codes
    )
    return (
        f'<div class="result-card">'
        f'<div class="result-rank">{rank:02d}</div>'
        f'<div class="result-name"><a href="{url}" target="_blank" rel="noopener">{name}</a></div>'
        f'<div class="result-types">{html.escape(type_names)}</div>'
        f'<div class="badge-row">{badges}</div>'
        f'</div>'
    )


def render_recommendations(recommendations: list[dict]) -> None:
    cards = "".join(render_result_card(i, r) for i, r in enumerate(recommendations, start=1))
    count = len(recommendations)
    html_out = (
        '<div class="shell-card results-wrap">'
        '<div class="results-head">'
        '<div>'
        '<div class="results-title">Final Shortlist</div>'
        f'<div class="results-copy">Exactly {count} grounded SHL recommendations, capped for evaluator-safe output.</div>'
        '</div>'
        '<div class="status-chip">Catalog URLs only</div>'
        '</div>'
        f'<div class="results-grid">{cards}</div>'
        '</div>'
    )
    st.markdown(html_out, unsafe_allow_html=True)


def render_transcript(messages: list[dict]) -> None:
    parts: list[str] = ['<div class="shell-card transcript">']
    for message in messages:
        role = "user" if message["role"] == "user" else "assistant"
        role_label = "Hiring Team" if role == "user" else "SHL Agent"
        css_class = "message message-user" if role == "user" else "message message-assistant"
        content = html.escape(message["content"]).replace("\n", "<br>")
        parts.append(
            f'<div class="{css_class}">'
            f'<span class="message-role">{role_label}</span>'
            f'{content}'
            f'</div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def submit_prompt(prompt: str) -> None:
    cleaned = prompt.strip()
    if not cleaned:
        return

    st.session_state.error_message = ""
    st.session_state.messages.append({"role": "user", "content": cleaned})

    try:
        with st.spinner("Preparing grounded recommendations..."):
            result = call_chat(st.session_state.messages)
    except Exception as exc:
        st.session_state.error_message = str(exc)
        st.session_state.messages.pop()
        return

    reply = result.get("reply", "")
    recommendations = result.get("recommendations", [])
    ended = bool(result.get("end_of_conversation", False))

    st.session_state.messages.append({"role": "assistant", "content": reply})
    if recommendations:
        st.session_state.recommendations = recommendations[:FINAL_TOP_K]
        st.session_state.show_recommendations = True
    else:
        st.session_state.show_recommendations = False

    # Never lock the conversation — ignore end_of_conversation flag
    # and do not cap on message count. User can always keep refining.
    st.session_state.ended = False
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "show_recommendations" not in st.session_state:
    st.session_state.show_recommendations = False
if "ended" not in st.session_state:
    st.session_state.ended = False
if "error_message" not in st.session_state:
    st.session_state.error_message = ""
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = ""

# Warm up the agent at the TOP of the page so the spinner never
# appears near the chat input bar. The first page load shows the
# spinner here; subsequent loads skip it (already cached).
if not API_URL:
    with st.spinner("Loading recommendation engine..."):
        get_agent()


with st.sidebar:
    st.markdown("## SHL Recommender")
    st.caption("A recruiter-friendly demo surface for the FastAPI recommender.")

    if st.button("Start New Conversation", use_container_width=True):
        reset_conversation()
        st.rerun()

    st.markdown("### Starter prompts")
    starters = [
        "I am hiring a senior full-stack Java engineer with AWS and Docker exposure.",
        "We need assessments for graduate financial analyst candidates.",
        "Help me shortlist tests for a bilingual healthcare administrator.",
    ]
    for starter in starters:
        if st.button(starter, key=f"starter_{starter[:24]}", use_container_width=True):
            reset_conversation()
            st.session_state.pending_prompt = starter
            st.rerun()

    st.markdown("### Assessment types")
    type_legend = [
        ("K", "Knowledge & Skills"),
        ("P", "Personality & Behavior"),
        ("A", "Ability & Aptitude"),
        ("C", "Competencies"),
        ("S", "Simulations"),
        ("E", "Assessment Exercises"),
        ("D", "Development & 360°"),
        ("B", "Biodata & Situational Judgment"),
    ]
    legend_html = '<div style="display:flex;flex-direction:column;gap:0.4rem;margin-top:0.3rem;">'
    for code, label in type_legend:
        legend_html += (
            f'<div style="display:flex;align-items:center;gap:0.55rem;">'
            f'<span style="min-width:1.6rem;height:1.6rem;display:inline-flex;align-items:center;'
            f'justify-content:center;border-radius:999px;background:rgba(183,135,46,0.13);'
            f'border:1px solid rgba(183,135,46,0.28);color:#8a6218;font-size:0.72rem;'
            f'font-weight:800;">{code}</span>'
            f'<span style="font-size:0.82rem;color:#241d17;font-weight:500;">{label}</span>'
            f'</div>'
        )
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)



pending_prompt = st.session_state.pending_prompt
if pending_prompt:
    st.session_state.pending_prompt = ""
    submit_prompt(pending_prompt)

st.markdown(
    '<div class="shell-card hero">'
    '<div class="hero-kicker">Conversational Assessment Selection</div>'
    '<h1>SHL recommendations with a cleaner final shortlist.</h1>'
    '<p>Describe the role in plain language, refine the brief naturally, and receive an exact final set of grounded SHL recommendations backed by catalog URLs.</p>'
    '<div class="pill-row">'
    '<div class="pill">Exact 10-result shortlist</div>'
    '<div class="pill">Stateless FastAPI workflow</div>'
    '<div class="pill">8-turn evaluator alignment</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

metric_columns = st.columns(3, gap="large")
metrics = [
    (
        "Shortlist",
        "Exactly 10 final recommendations",
        "The UI surfaces a complete, recruiter-friendly top 10 whenever the agent commits.",
    ),
    (
        "Behavior",
        "Clarify, refine, compare, refuse",
        "The conversation stays scoped to SHL assessments and remains stateless for evaluation.",
    ),
    (
        "Deployment",
        "Streamlit for demo, FastAPI for scoring",
        "The frontend is ideal for presentation, while the evaluator should hit the API directly.",
    ),
]
for column, (label, value, copy) in zip(metric_columns, metrics):
    with column:
        st.markdown(
            f'<div class="shell-card metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'<div class="metric-copy">{copy}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

turns_used = len(st.session_state.messages)

status_title = "Conversation ready" if turns_used == 0 else "In progress"
status_copy = "Start with the role, seniority, or constraints you already know." if turns_used == 0 else f"{turns_used // 2} exchange{'s' if turns_used // 2 != 1 else ''} so far — keep refining or ask for a shortlist."
status_chip = "Listening"

st.markdown(
    f'<div class="status-bar">'
    f'<div>'
    f'<div class="status-title">{status_title}</div>'
    f'<div class="status-copy">{status_copy}</div>'
    f'</div>'
    f'<div class="status-chip">{status_chip}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

if st.session_state.error_message:
    st.error(st.session_state.error_message)

if st.session_state.messages:
    render_transcript(st.session_state.messages)
else:
    st.markdown(
        '<div class="shell-card empty-state">'
        '<h3>Start with the hiring brief.</h3>'
        '<p>You can describe the role, mention the level, add constraints like language or remote testing, or use one of the starter prompts from the sidebar.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

if st.session_state.show_recommendations and st.session_state.recommendations:
    render_recommendations(st.session_state.recommendations)

placeholder = "Describe the role, constraints, or refinement you want to make..."
if st.session_state.show_recommendations:
    placeholder = "Refine the shortlist, compare assessments, or confirm the current set..."

user_input = st.chat_input(
    placeholder,
    disabled=False,
)

if user_input:
    submit_prompt(user_input)

