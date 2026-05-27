import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# CSS for Terminal Style
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar: Control Room & AI Analyst ---
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    
    # 1. DYNAMIC MATH PARAMETERS
    LEAGUE_PARAMS = {
        "nba": {"pace": 2.15, "baseline": 55.5, "name": "NBA"},
        "wnba": {"pace": 1.95, "baseline": 41.5, "name": "WNBA"}
    }
    p = LEAGUE_PARAMS[league]
    
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"): st.markdown(f"Analysis: Evaluating {p['name']} variance metrics...")

# --- Main Tabs ---
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        st.title(f"🏀 {p['name']} Arbitrage Terminal")
        
        # ACTIVE QUARTER ANALYTICS (Math depends on p['baseline'])
        st.markdown("#### 🎯 Active Quarter Analytics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Scoreboard", "53 - 37", delta="IND vs POR")
        c2.metric("Live Market Line", f"{p['baseline']} pts", delta="Current Market Total")
        c3.metric("Live Quarter Total", "42 pts", delta="Q2 Running")
        c4.metric("Current Game Total", "90 pts", delta="Combined Score")
        
        # MACRO GAME-FLOW (Math depends on p['pace'])
        st.markdown("#### 🧠 Macro Game-Flow Guide")
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Mirror Projection", f"{42 * p['pace']:.1f} pts", delta="Engine Prediction")
        g2.metric("1H Projection", f"{80 * p['pace']:.1f} pts", delta="Pacing Adjusted")
        g3.metric("Full Game Projection", f"{160 * p['pace']:.1f} pts", delta="Projected Total")
        g4.metric("Target Adjusted Pacing", f"{42 * 1.5:.1f} pts", delta="Benchmark")

        # VARIANCE MATRIX
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        df = pd.DataFrame([{"Platform": "📈 Polymarket", "Total": 40.5, "Odds": "-110", "Signal": "📈 OVER"}])
        st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;' if "OVER" in x else '', subset=['Signal']), 
                     use_container_width=True, hide_index=True)
    
    render_live_terminal()

with tab2:
    st.subheader(f"🗓️ {p['name']} Archive & Outlook")
    # 2. FILTERED HISTORY
    # Only show history matching the selected league
    history_df = pd.DataFrame([
        {"League": "nba", "Game": "Lakers vs. Celtics", "Outcome": "Hit"},
        {"League": "wnba", "Game": "Aces vs. Sky", "Outcome": "Hit"}
    ])
    filtered_history = history_df[history_df["League"] == league]
    st.dataframe(filtered_history, use_container_width=True)
