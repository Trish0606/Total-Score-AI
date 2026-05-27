import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# --- CUSTOM TERMINAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROL ROOM & AI ---
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    
    # League Constants
    params = {"nba": {"pace": 2.15, "baseline": 55.5}, "wnba": {"pace": 1.95, "baseline": 41.5}}[league]
    
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"): st.markdown(f"Analysis: Evaluating {league.upper()} variance...")

# --- MAIN DASHBOARD ---
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        # Fetching Live Matchup Data
        live_data = fetch_live_scores(league) 
        matchup = live_data.get('matchup', 'No Active Game')
        score = live_data.get('score', '0 - 0')
        q_total = live_data.get('quarter_total', 42)
        
        st.title(f"🏀 {league.upper()} Arbitrage Terminal")
        st.subheader(f"Current Matchup: {matchup}")
        
        # ROW 1: Active Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Score", score, delta="Active Game")
        c2.metric("Market Line", f"{params['baseline']} pts", delta="Live Odds")
        c3.metric("Quarter Total", f"{q_total} pts", delta="Pacing")
        c4.metric("Game Total", "90 pts", delta="Combined")
        
        # ROW 2: Macro Guide
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Mirror Projection", f"{q_total * params['pace']:.1f} pts", delta="Engine")
        g2.metric("1H Projection", "90.0 pts", delta="Adjusted")
        g3.metric("Full Projection", "180.0 pts", delta="Total")
        g4.metric("Pacing Benchmark", "63.0 pts", delta="Target")

        # ROW 3: Variance Matrix
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        platforms = [
            {"Platform": "📈 Polymarket", "Total": 40.5, "Signal": "📈 OVER"},
            {"Platform": "👑 DraftKings", "Total": 41.5, "Signal": "📈 OVER"}
        ]
        df = pd.DataFrame(platforms)
        st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;' if "OVER" in x else '', subset=['Signal']), 
                     use_container_width=True, hide_index=True)
    
    render_live_terminal()

with tab2:
    st.subheader(f"🗓️ {league.upper()} Archive & Outlook")
    # Filtered History
    history = pd.DataFrame({"Game": ["Aces vs Sky"], "Outcome": ["Hit"], "League": ["wnba"]})
    st.dataframe(history[history["League"] == league], use_container_width=True)
