import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# Modern Terminal CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    # Dynamic Constants
    params = {"nba": {"pace": 2.15, "baseline": 55.5}, "wnba": {"pace": 1.95, "baseline": 41.5}}[league]

# Main Terminal
st.title(f"🏀 {league.upper()} Arbitrage Terminal")

# ROW 1: Active Quarter Analytics (WITH DELTAS)
st.markdown("#### 🎯 Active Quarter Analytics")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Scoreboard", "53 - 37", delta="IND vs POR")
c2.metric("Live Market Line", f"{params['baseline']} pts", delta="Current Market Total")
c3.metric("Live Quarter Total", "42 pts", delta="Q2 Running")
c4.metric("Current Game Total", "90 pts", delta="Combined Score")

# ROW 2: Macro Game-Flow (WITH DELTAS)
st.markdown("#### 🧠 Macro Game-Flow Guide")
g1, g2, g3, g4 = st.columns(4)
g1.metric("Mirror Projection", "84.0 pts", delta="Engine Prediction")
g2.metric("1H Projection", "90.0 pts", delta="Pacing Adjusted")
g3.metric("Full Game Projection", "180.0 pts", delta="Projected Total")
g4.metric("Target Adjusted Pacing", "63.0 pts", delta="Benchmark")

# VARIANCE MATRIX
st.markdown("#### 📊 Multi-Platform Variance Matrix")
platforms = [
    {"Platform": "📈 Polymarket", "Total": 40.5, "Odds": "-110", "Signal": "📈 OVER"},
    {"Platform": "👑 DraftKings", "Total": 41.5, "Odds": "-115", "Signal": "📈 OVER"},
    {"Platform": "🦁 BetMGM", "Total": 41.0, "Odds": "-110", "Signal": "📈 OVER"}
]

df = pd.DataFrame(platforms)
st.dataframe(df.style.map(
    lambda x: 'color: #00ff41; font-weight: bold;' if "OVER" in x else '', subset=['Signal']), 
    use_container_width=True, hide_index=True)
