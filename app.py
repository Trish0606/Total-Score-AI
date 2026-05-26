import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# Custom CSS for the Terminal Look
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
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    if prompt := st.chat_input("Ask for prediction help..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Placeholder for AI Response logic
        st.session_state.messages.append({"role": "assistant", "content": "Analysis: High variance detected in Q2."})

# Tabs
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        st.title(f"🏀 {league.upper()} Arbitrage Terminal")
        
        # ACTIVE QUARTER ANALYTICS
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Scoreboard", "53 - 37", delta="IND vs POR")
        c2.metric("Live Market Line", "41.5 pts", delta="Current Market Total")
        c3.metric("Live Quarter Total", "42 pts", delta="Q2 Running")
        c4.metric("Current Game Total", "90 pts", delta="Combined Score")
        
        # VARIANCE MATRIX WITH MORE PLATFORMS
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        # Expanded list of platforms
        platforms = {
            "📈 Polymarket": {"total": 40.5, "odds": "-110"},
            "🏛️ Kalshi": {"total": 39.5, "odds": "-105"},
            "👑 DraftKings": {"total": 41.5, "odds": "-115"},
            "🦁 BetMGM": {"total": 41.0, "odds": "-110"},
            "🍀 FanDuel": {"total": 42.0, "odds": "-112"},
            "🏛️ Caesars": {"total": 41.0, "odds": "-110"}
        }

        data = []
        mirror_pred = 84.0 # Replace with your dynamic calculation
        for name, val in platforms.items():
            var = mirror_pred - val['total']
            data.append({
                "Platform": name,
                "Live Market Total": val['total'],
                "Live Odds": val['odds'],
                "Variance": f"{var:.1f}",
                "Signal": "📈 OVER" if var > 1.5 else ("📉 UNDER" if var < -1.5 else "➖ NEUTRAL")
            })
            
        st.dataframe(pd.DataFrame(data).style.map(
            lambda x: 'color: #00ff41; font-weight: bold;' if x == "📈 OVER" else ('color: #ff4d4d; font-weight: bold;' if x == "📉 UNDER" else ''), 
            subset=['Signal']), 
            use_container_width=True, hide_index=True)
    
    render_live_terminal()

with tab2:
    st.subheader("🗓️ Game Archive & Outlook")
    st.write("Historical outcomes and upcoming schedules will appear here.")
