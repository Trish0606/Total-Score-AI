import streamlit as st
import pandas as pd
from src.ingestion import get_processed_game_data, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# --- CSS FOR TERMINAL STYLE ---
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

# --- MAIN TERMINAL ---
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        active_games = get_processed_game_data(league)
        
        if not active_games:
            st.info("No active games found right now.")
            return

        for game in active_games:
            st.title(f"🏀 {game['name']} Arbitrage Terminal")
            
            # MATH ENGINE INTEGRATION
            q_total = game["q_total"]
            # Velocity logic based on your 5-pt-per-minute rule
            proj_q = q_total + (float(game["clock"].split(":")[0]) * 5)
            
            # METRICS WITH GREEN DELTAS
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Live Scoreboard", game["total"], delta="Active Match")
            c2.metric("Market Line", f"{params['baseline']} pts", delta="Current Odds")
            c3.metric("Quarter Total", q_total, delta="Q-Pacing")
            c4.metric("AI Projection", round(proj_q, 1), delta="Velocity Rule")
            
            # VARIANCE MATRIX
            st.markdown("#### 📊 Multi-Platform Variance Matrix")
            # List of platforms you monitor
            platforms = [
                {"Platform": "📈 Polymarket", "Line": 40.5, "Signal": "📈 OVER"},
                {"Platform": "👑 DraftKings", "Line": 41.5, "Signal": "📈 OVER"},
                {"Platform": "🦁 BetMGM", "Line": 41.0, "Signal": "📈 OVER"}
            ]
            df = pd.DataFrame(platforms)
            st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;' if "OVER" in x else '', subset=['Signal']), 
                         use_container_width=True, hide_index=True)
            
            # LIVE ALERTS
            if game["clock"] == "6:00": st.warning(f"🚨 6-MIN MIRROR TRIGGER: {q_total * 2}")

    render_live_terminal()

with tab2:
    st.subheader(f"🗓️ {league.upper()} Archive & Outlook")
    history = pd.DataFrame({"Game": ["Aces vs Sky"], "Outcome": ["Hit"], "League": ["wnba"]})
    st.dataframe(history[history["League"] == league], use_container_width=True)
