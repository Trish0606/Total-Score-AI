import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# Custom Terminal Styling
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar with AI Chat
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
        response = "AI Analysis: The current pacing indicates high volatility. Monitor the variance."
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)

# Tabbed Layout
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        st.title(f"🏀 {league.upper()} Arbitrage Terminal")
        # Logic to display your Live Scoreboard, Pacing, and Variance Matrix
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Score", "19 - 13", delta="Q1 Running")
        c2.metric("Mirror Projection", "64.0 pts")
        c3.metric("Baseline", "41.5 pts")
        c4.metric("Market Status", "VOLATILE")
        
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        df = pd.DataFrame([
            {"Platform": "📈 Polymarket", "Line": 40.5, "Var": 23.5, "Signal": "OVER"},
            {"Platform": "👑 DraftKings", "Line": 41.5, "Var": 22.5, "Signal": "OVER"}
        ])
        st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;', subset=['Signal']), 
                     use_container_width=True, hide_index=True)
    
    render_live_terminal()

with tab2:
    st.subheader("🗓️ Game Archive & Outlook")
    st.markdown("#### Upcoming Games")
    st.table(pd.DataFrame({"Game": ["Aces vs. Sky"], "Tip-Off": ["8:00 PM"]}))
    st.markdown("#### Past Performance")
    st.dataframe(pd.DataFrame({"Game": ["Fire vs. Fever"], "Outcome": ["Hit"]}))
