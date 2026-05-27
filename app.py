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
    
    # Configuration profiles handling WNBA (40 mins) vs NBA (48 mins)
    params = {
        "nba": {"pace": 2.15, "baseline": 220.5, "mins": 48.0}, 
        "wnba": {"pace": 1.95, "baseline": 165.5, "mins": 40.0}
    }[league]
    
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: 
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): 
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)

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
            status = game.get("status", "SCHEDULED").upper()
            st.title(f"🏀 {game['name']} Arbitrage Terminal")
            
            # --- CASE 1: GAME IS CURRENTLY LIVE ---
            if status in ["IN_PROGRESS", "LIVE", "1Q", "2Q", "3Q", "4Q", "HALFTIME"]:
                clock_val = game.get("clock", "10:00")
                parts = clock_val.split(":") if ":" in clock_val else ["0", "0"]
                elapsed_mins = params["mins"] - (float(parts[0]) + (float(parts[1]) / 60.0))
                
                # Protect against division by zero at the exact start of a game
                pace_factor = game["total"] / elapsed_mins if elapsed_mins > 0.5 else 0
                pace_projection = pace_factor * params["mins"]

                # ROW 1: GAME FLOW ANALYTICS
                st.markdown(f"#### 🎯 Game Flow Analytics (Status: {status})")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("1H Total", f"{game.get('1h_score', 0)} pts", delta="First Half")
                c2.metric("Total Score", game['total'], delta="Current Game")
                c3.metric("Pace Index", f"{pace_factor:.2f}", delta="Pts/Min Velocity")
                c4.metric("AI Pace Prediction", round(pace_projection, 1), delta="Projected Final")
                
                # ROW 2: MACRO PROJECTIONS
                st.markdown("#### 🧠 Macro Game-Flow Guide")
                g1, g2, g3, g4 = st.columns(4)
                g1.metric("Baseline Projection", f"{params['baseline']} pts", delta="Market")
                g2.metric("Velocity Adjusted", f"{round(pace_projection, 1)} pts", delta="Calculated")
                g3.metric("H2 Forecast", f"{round(pace_projection * 0.5, 1)}")
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

            # --- CASE 2: GAME HAS NOT STARTED YET ---
            elif status in ["SCHEDULED", "PRE", "PRE_GAME"]:
                st.warning(f"⏳ This matchup is scheduled but has not tipped off yet.")
                st.markdown("#### 🧠 Pre-Match Projections")
                c1, c2 = st.columns(2)
                c1.metric("Market Baseline Total", f"{params['baseline']} pts")
                c2.metric("Target Pace Environment", f"{params['pace']} pts/min")
                st.info("Live velocity tracking and variance matrix signals will activate dynamically once the game clock begins.")

            # --- CASE 3: GAME IS ALREADY OVER ---
            elif status in ["FINAL", "FINISHED", "DONE"]:
                st.success("🏁 This event is complete.")
                st.markdown("#### 📊 Final Post-Game Summary")
                c1, c2 = st.columns(2)
                c1.metric("Final Score Total", game.get('total', 'N/A'))
                c2.metric("Market Line Closing Delta", f"{round(game.get('total', 0) - params['baseline'], 1)}")

    render_live_terminal()

with tab2:
    st.subheader(f"🗓️ {league.upper()} Archive & Outlook")
