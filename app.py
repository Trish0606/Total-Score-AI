import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores 

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# Custom CSS for the terminal look
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# 1. League-Specific Constants
LEAGUE_PARAMS = {
    "nba": {"pace": 2.15, "baseline": 55.5},
    "wnba": {"pace": 1.95, "baseline": 41.5}
}

# 2. Sidebar: Control Room & AI Analyst
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    params = LEAGUE_PARAMS[league]
    
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

# 3. Main Dashboard
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    # Display the specific teams playing (Replace with your dynamic variable)
    st.title(f"🏀 {league.upper()} Arbitrage Terminal")
    st.subheader("IND vs POR | Live") 
    
    # ROW 1: Active Quarter Analytics (WITH GREEN DELTAS)
    st.markdown("#### 🎯 Active Quarter Analytics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Scoreboard", "53 - 37", delta="IND vs POR")
    c2.metric("Live Market Line", f"{params['baseline']} pts", delta="Current Market Total")
    c3.metric("Live Quarter Total", "42 pts", delta="Q2 Running")
    c4.metric("Current Game Total", "90 pts", delta="Combined Score")
    
    # ROW 2: Macro Game-Flow (WITH GREEN DELTAS)
    st.markdown("#### 🧠 Macro Game-Flow Guide")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Mirror Projection", "84.0 pts", delta="Engine Prediction")
    g2.metric("1H Projection", "9
