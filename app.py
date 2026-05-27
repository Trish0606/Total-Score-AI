import streamlit as st
import pandas as pd
from src.ingestion import get_processed_game_data

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# --- CSS TERMINAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    params = {"nba": {"pace": 2.15, "baseline": 220.5}, "wnba": {"pace": 1.95, "baseline": 165.5}}[league]
    
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
            st.info("No active games right now.")
            return

        for game in active_games:
            st.title(f"🏀 {game['name']} Arbitrage Terminal")
            
            # SAFE CLOCK PROCESSING (Prevents IndexError)
            clock_val = game.get("clock", "0:00")
            parts = clock_val.split(":") if ":" in clock_val else ["0", "0"]
            elapsed_mins = 48.0 - (float(parts[0]) + (float(parts[1]) / 60.0))
            pace_factor = game["total"] / elapsed_mins if elapsed_mins > 1 else 0
            pace_projection = pace_factor * 48

            # ROW 1: GAME FLOW ANALYTICS
            st.markdown("#### 🎯 Game Flow Analytics")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("1H Total", "52 pts", delta="First Half")
            c2.metric("Total Score", game['total'], delta="Current Game")
            c3.metric("Pace Index", f"{pace_factor:.2f}", delta="Pts/Min Velocity")
            c4.metric("AI Pace Prediction", round(pace_projection, 1), delta="Projected Final")
            
            # ROW 2: MACRO PROJECTIONS
            st.markdown("#### 🧠 Macro Game-Flow Guide")
            g1, g2, g3, g4 = st.columns(4)
            g1.metric("Baseline Projection", f"{params['baseline']} pts", delta="Market")
            g2.metric("Velocity Adjusted", f"{round(pace_projection, 1)} pts", delta="Calculated")
            g3.metric("1H Multiplier", f"{round(pace_projection * 0.55, 1)}", delta="H2 Forecast")
            g4.metric("Variance Delta", f"{round(pace_projection - params['baseline'], 1)}", delta="Edge")

            # ROW 3: VARIANCE MATRIX
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
