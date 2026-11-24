import os
import sys
import time
from pathlib import Path
import streamlit as st

# Ensure the module directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from pipeline import (
    run_search_step,
    run_reader_step,
    run_writer_step,
    run_critic_step,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

.stApp {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 50% at 20% -10%, rgba(255,140,50,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 110%, rgba(255,80,30,0.08) 0%, transparent 55%);
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin: 0 0 1rem;
}
.hero h1 span {
    color: #ff8c32;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #a09890;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 2rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,140,50,0.15);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(8px);
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,140,50,0.25) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 0 3px rgba(255,140,50,0.12) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

/* ── Primary Action Button ── */
.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.04em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s !important;
    box-shadow: 0 4px 20px rgba(255,140,50,0.3) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(255,140,50,0.4) !important;
    opacity: 0.95 !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, background 0.3s;
}
.step-card.active {
    border-color: rgba(255,140,50,0.5);
    background: rgba(255,140,50,0.06);
    box-shadow: 0 0 15px rgba(255,140,50,0.15);
}
.step-card.done {
    border-color: rgba(80,200,120,0.4);
    background: rgba(80,200,120,0.04);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.08);
    transition: background 0.3s;
}
.step-card.active::before { background: #ff8c32; }
.step-card.done::before   { background: #50c878; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #ff8c32;
    opacity: 0.8;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: #f0ebe0;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    font-weight: 600;
}
.status-waiting  { color: #666; }
.status-running  { color: #ff8c32; animation: blink 1.2s infinite; }
.status-done     { color: #50c878; }

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}
.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.result-content {
    font-size: 0.92rem;
    line-height: 1.8;
    color: #cdc8bf;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

/* ── Report & feedback panels ── */
.report-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,140,50,0.25);
    border-radius: 16px;
    padding: 2.2rem 2.5rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(80,200,120,0.25);
    border-radius: 16px;
    padding: 2.2rem 2.5rem;
    margin-top: 1.5rem;
}
.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
    font-weight: 600;
}
.panel-label.orange {
    color: #ff8c32;
    border-bottom: 1px solid rgba(255,140,50,0.2);
}
.panel-label.green {
    color: #50c878;
    border-bottom: 1px solid rgba(80,200,120,0.2);
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0ebe0;
    margin: 1.5rem 0 1rem;
}

.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #605850;
    text-align: center;
    margin-top: 3.5rem;
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ── Pipeline steps definition ─────────────────────────────────────────────────
PIPELINE_STEPS = [
    ("search", "01", "Search Agent",  "Gathers recent & reliable web info"),
    ("reader", "02", "Reader Agent",  "Scrapes & extracts deep content"),
    ("writer", "03", "Writer Chain",  "Drafts the full research report"),
    ("critic", "04", "Critic Chain",  "Reviews & scores the final report"),
]


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("WAITING", "status-waiting"))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.8rem;color:#857e75;margin-top:0.3rem;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
if "results" not in st.session_state:
    st.session_state["results"] = {}
if "topic_query" not in st.session_state:
    st.session_state["topic_query"] = ""


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a comprehensive, polished research report.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic_val = st.text_input(
        "Research Topic",
        value=st.session_state["topic_query"],
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Interactive example chips
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:0.7rem;color:#ff8c32;letter-spacing:0.12em;margin-bottom:0.5rem;">TRY AN EXAMPLE:</div>', unsafe_allow_html=True)
    chip_cols = st.columns(3)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    for i, ex in enumerate(examples):
        if chip_cols[i].button(ex, key=f"chip_{i}", use_container_width=True):
            st.session_state["topic_query"] = ex
            st.rerun()


# ── Right column: Pipeline Status cards placeholder ───────────────────────────
pipeline_placeholder = col_pipeline.empty()


def render_pipeline(active_step=None):
    """Render the 4 pipeline cards based on current session state & active step."""
    r = st.session_state.get("results", {})
    with pipeline_placeholder.container():
        st.markdown('<div class="section-heading">Pipeline Status</div>', unsafe_allow_html=True)
        for key, num, title, desc in PIPELINE_STEPS:
            if key in r:
                state = "done"
            elif key == active_step:
                state = "running"
            else:
                state = "waiting"
            step_card(num, title, state, desc)


# Initial render of the pipeline cards
render_pipeline(active_step=None)


# ── Pipeline Execution ────────────────────────────────────────────────────────
status_area = st.empty()

if run_btn:
    chosen_topic = topic_val.strip() if topic_val else ""
    if not chosen_topic:
        st.warning("⚠️ Please enter a research topic to begin.")
    else:
        # Reset previous results
        st.session_state["results"] = {}
        st.session_state["topic_query"] = chosen_topic
        results = {}

        try:
            # ── Step 1: Search Agent ──
            render_pipeline(active_step="search")
            with status_area.container():
                with st.spinner("🔍 Step 1/4: Search Agent is discovering relevant sources..."):
                    search_res = run_search_step(chosen_topic)
                    results["search"] = search_res
                    st.session_state["results"] = dict(results)

            # ── Step 2: Reader Agent ──
            render_pipeline(active_step="reader")
            with status_area.container():
                with st.spinner("📄 Step 2/4: Reader Agent is extracting in-depth content..."):
                    reader_res = run_reader_step(chosen_topic, search_res)
                    results["reader"] = reader_res
                    st.session_state["results"] = dict(results)

            # ── Step 3: Writer Chain ──
            render_pipeline(active_step="writer")
            with status_area.container():
                with st.spinner("✍️ Step 3/4: Writer Chain is synthesizing and structuring the report..."):
                    writer_res = run_writer_step(chosen_topic, search_res, reader_res)
                    results["writer"] = writer_res
                    st.session_state["results"] = dict(results)

            # ── Step 4: Critic Chain ──
            render_pipeline(active_step="critic")
            with status_area.container():
                with st.spinner("🧐 Step 4/4: Critic Chain is assessing quality and giving feedback..."):
                    critic_res = run_critic_step(writer_res)
                    results["critic"] = critic_res
                    st.session_state["results"] = dict(results)

            # All finished
            render_pipeline(active_step=None)
            with status_area.container():
                st.success("✅ Research report generated successfully!")

        except Exception as err:
            render_pipeline(active_step=None)
            with status_area.container():
                st.error(f"❌ Error during pipeline execution: {str(err)}")


# ── Results display ───────────────────────────────────────────────────────────
res = st.session_state.get("results", {})

if res:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Research Output</div>', unsafe_allow_html=True)

    # Raw Search Agent Output
    if "search" in res:
        with st.expander("🔍 Search Agent Findings (Raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel">'
                f'<div class="result-panel-title">Search Agent Output</div>'
                f'<div class="result-content">{res["search"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Raw Reader Agent Scraped Output
    if "reader" in res:
        with st.expander("📄 Reader Agent Extracted Content (Raw)", expanded=False):
            st.markdown(
                f'<div class="result-panel">'
                f'<div class="result-panel-title">Reader Agent Output</div>'
                f'<div class="result-content">{res["reader"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Final Writer Report
    if "writer" in res:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label orange">📝 Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(res["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Download button
        st.download_button(
            label="⬇  Download Report (.md)",
            data=res["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
            use_container_width=False,
        )

    # Critic Review & Feedback
    if "critic" in res:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label green">🧐 Critic Evaluation & Scoring</div>
        """, unsafe_allow_html=True)
        st.markdown(res["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Multi-Agent Research System Powered by LangChain, Groq & Tavily · Streamlit
</div>
""", unsafe_allow_html=True)
