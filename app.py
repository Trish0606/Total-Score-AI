import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- Sidebar Logic ---
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select League", ["nba", "wnba"])
    
    # Define league-specific constants
    LEAGUE_PARAMS = {
        "nba": {"pace": 2.15, "baseline": 55.5},
        "wnba": {"pace": 1.95, "baseline": 41.5}
    }
    params = LEAGUE_PARAMS[league]
    
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"): st.markdown("Analysis: Monitoring variance across all platforms...")

# --- Main Dashboard ---
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        st.title(f"🏀 {league.upper()} Arbitrage Terminal")
        
        # Calculations derived from selection
        q_total = 42 # Example: fetched from your live data
        mirror_pred = q_total * params["pace"]
        
        # Row 1: Active Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Scoreboard", "53 - 37")
        c2.metric("Live Market Line", f"{params['baseline']} pts")
        c3.metric("Live Quarter Total", f"{q_total} pts")
        c4.metric("Current Game Total", "90 pts")
        
        # Row 2: Macro
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Mirror Projection", f"{mirror_pred:.1f} pts")
        g2.metric("1H Projection", f"{mirror_pred * 1.1:.1f} pts")
        g3.metric("Full Game Projection", f"{mirror_pred * 2:.1f} pts")
        g4.metric("Target Pacing", f"{q_total * 1.5:.1f} pts")

        # Row 3: Variance Matrix
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        platforms = [
            {"Platform": "📈 Polymarket", "Total": 40.5, "Odds": "-110"},
            {"Platform": "👑 DraftKings", "Total": 41.5, "Odds": "-115"},
            {"Platform": "🦁 BetMGM", "Total": 41.0, "Odds": "-110"}
        ]
        
        data = []
        for p in platforms:
            var = mirror_pred - p["Total"]
            data.append({**p, "Variance": f"{var:.1f}", "Signal": "📈 OVER" if var > 1.5 else "➖ NEUTRAL"})
        
        st.dataframe(pd.DataFrame(data).style.map(
            lambda x: 'color: #00ff41; font-weight: bold;' if "OVER" in x else '', subset=['Signal']),
            use_container_width=True, hide_index=True)
    
    render_live_terminal()

with tab2:
    st.subheader("🗓️ Game Archive & Outlook")
    st.markdown("#### Upcoming Games")
    st.table(pd.DataFrame({"Game": ["Aces vs. Sky"], "Tip-Off": ["8:00 PM"]}))
