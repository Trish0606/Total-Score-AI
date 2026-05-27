import streamlit as st
import pandas as pd
from src.ingestion import get_processed_game_data

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# --- CUSTOM TERMINAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROL & AI ---
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
            
            q_total = game["q_total"]
            proj_q = q_total + (float(game["clock"].split(":")[0]) * 5)
            
            # ROW 1: ACTIVE QUARTER ANALYTICS (Deltas Included)
            st.markdown("#### 🎯 Active Quarter Analytics")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Live Scoreboard", game['total'], delta="Active Match")
            c2.metric("Market Line", f"{params['baseline']} pts", delta="Current Odds")
            c3.metric("Quarter Total", q_total, delta="Q-Pacing")
            c4.metric("AI Projection", round(proj_q, 1), delta="Velocity Rule")
            
            # ROW 2: MACRO GAME-FLOW GUIDE
            st.markdown("#### 🧠 Macro Game-Flow Guide")
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Mirror Projection", f"{q_total * params['pace']:.1f} pts", delta="Engine Prediction")
            g2.metric("1H Projection", f"{q_total * params['pace'] * 1.1:.1f} pts", delta="Pacing Adjusted")
            g3.metric("Full Game Projection", f"{q_total * params['pace'] * 2:.1f} pts", delta="Projected Total")
            g4.metric("Target Adjusted Pacing", f"{q_total * 1.5:.1f} pts", delta="Benchmark")

            # ROW 3: EXPANDED VARIANCE MATRIX
            st.markdown("#### 📊 Multi-Platform Variance Matrix")
            platforms = [
                {"Platform": "📈 Polymarket", "Total": 40.5, "Signal": "📈 OVER"},
                {"Platform": "👑 DraftKings", "Total": 41.5, "Signal": "📈 OVER"},
                {"Platform": "🦁 BetMGM", "Total": 41.0, "Signal": "📈 OVER"},
                {"Platform": "🔥 FanDuel", "Total": 42.0, "Signal": "📈 OVER"}
            ]
            df = pd.DataFrame(platforms)
            st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;' if "OVER" in x else '', subset=['Signal']), 
                         use_container_width=True, hide_index=True)

    render_live_terminal()

with tab2:
    st.subheader(f"🗓️ {league.upper()} Archive & Outlook")
