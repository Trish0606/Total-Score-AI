import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores, fetch_schedule 

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# 1. Sidebar Controls
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select League", ["nba", "wnba"])
    st.divider()
    st.header("🤖 AI Analyst")
    prompt = st.chat_input("Ask about predictions...")

# 2. Main Tabbed Layout
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

# --- TAB 1: LIVE TERMINAL ---
with tab1:
    @st.fragment(run_every=10)
    def render_live_terminal():
        st.subheader(f"Current Live {league.upper()} Monitor")
        # [Insert your existing live dashboard logic here]
        # Keep your current columns, metrics, and variance matrix
        st.info("Live data stream active...")

    render_live_terminal()

# --- TAB 2: ARCHIVE & OUTLOOK ---
with tab2:
    st.subheader("🗓️ Next Games & Historical Outcomes")
    
    # Next Games Module
    st.markdown("#### ⏳ Upcoming Schedule")
    # next_games = fetch_schedule(league) 
    st.table(pd.DataFrame({"Game": ["Aces vs. Sky", "Liberty vs. Sun"], "Tip-Off": ["8:00 PM", "10:00 PM"]}))
    
    # Historical Performance Module
    st.markdown("#### 📈 Past Predictions & Hit Rate")
    history_df = pd.DataFrame([
        {"Game": "Fire at Fever", "Engine Prediction": 50.0, "Actual Outcome": 52.0, "Hit": "✅"},
        {"Game": "Wings at Lynx", "Engine Prediction": 45.5, "Actual Outcome": 44.0, "Hit": "✅"}
    ])
    st.dataframe(history_df, use_container_width=True)

# 3. Footer / Status
st.divider()
st.caption("Terminal v2.0 | High-Frequency Arbitrage Mode Enabled")
