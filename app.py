import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# Modern Terminal CSS
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"): st.markdown("Analysis: Monitoring variance across all books...")

# Tabs
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        st.title(f"🏀 {league.upper()} Arbitrage Terminal")
        
        # ROW 1: Active Quarter Analytics
        st.markdown("#### 🎯 Active Quarter Analytics")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Scoreboard", "53 - 37", delta="IND vs POR")
        c2.metric("Live Market Line", "41.5 pts", delta="Current Market Total")
        c3.metric("Live Quarter Total", "42 pts", delta="Q2 Running")
        c4.metric("Current Game Total", "90 pts", delta="Combined Score")
        
        # ROW 2: Macro Game-Flow
        st.markdown("#### 🧠 Macro Game-Flow Guide")
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("Mirror Projection", "84.0 pts")
        g2.metric("1H Projection", "90.0 pts")
        g3.metric("Full Game Projection", "180.0 pts")
        g4.metric("Target Adjusted Pacing", "63.0 pts")

        # VARIANCE MATRIX
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        platforms = {
            "📈 Polymarket": {"total": 40.5, "odds": "-110"},
            "👑 DraftKings": {"total": 41.5, "odds": "-115"},
            "🦁 BetMGM": {"total": 41.0, "odds": "-110"},
            "🍀 FanDuel": {"total": 42.0, "odds": "-112"}
        }
        
        data = [{"Platform": k, "Total": v['total'], "Odds": v['odds'], "Signal": "OVER"} for k, v in platforms.items()]
        df = pd.DataFrame(data)
        st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;', subset=['Signal']), 
                     use_container_width=True, hide_index=True)
    
    render_live_terminal()

with tab2:
    st.subheader("🗓️ Game Archive & Outlook")
    st.markdown("#### Upcoming Games")
    st.table(pd.DataFrame({"Game": ["Aces vs. Sky"], "Tip-Off": ["8:00 PM"]}))
