import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# Custom CSS for the Terminal Look
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("Ask for prediction help..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # Your AI Logic Here
        st.session_state.messages.append({"role": "assistant", "content": "Analysis: High variance detected in Q2."})
        with st.chat_message("assistant"): st.markdown("Analysis: High variance detected in Q2.")

# Tabs
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        st.title(f"🏀 {league.upper()} Arbitrage Terminal")
        
        # ACTIVE QUARTER ANALYTICS (As requested)
        st.markdown("#### 🎯 Active Quarter Analytics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Scoreboard", "53 - 37", delta="IND vs POR")
        c2.metric("Live Market Line", "41.5 pts", delta="Current Market Total")
        c3.metric("Live Quarter Total", "42 pts", delta="Q2 Running")
        c4.metric("Current Game Total", "90 pts", delta="Combined Score")
        
        # MACRO GAME FLOW
        st.markdown("#### 🧠 Macro Game-Flow Guide")
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Mirror Projection", "84.0 pts")
        g2.metric("1H Projection", "90.0 pts")
        g3.metric("Full Game Projection", "180.0 pts")
        g4.metric("Target Adjusted Pacing", "63.0 pts")

        # VARIANCE MATRIX
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        df = pd.DataFrame([
            {"Platform": "📈 Polymarket", "Live Market Total": 40.5, "Live Odds": -110, "Variance": 43.5, "Signal": "OVER"},
            {"Platform": "👑 DraftKings", "Live Market Total": 41.5, "Live Odds": -115, "Variance": 42.5, "Signal": "OVER"}
        ])
        st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;', subset=['Signal']), 
                     use_container_width=True, hide_index=True)
    
    render_live_terminal()

with tab2:
    st.subheader("🗓️ Game Archive & Outlook")
    # Add your logic for schedule and history here
    st.write("Historical outcomes and upcoming schedules will appear here.")
