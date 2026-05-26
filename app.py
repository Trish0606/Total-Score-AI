import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores

# 1. Page Config
st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# 2. Custom CSS for "Terminal" Look
st.markdown("""
    <style>
    .card { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px; }
    .stApp { background-color: #050505; }
    </style>
    """, unsafe_allow_html=True)

# 3. Sidebar Controls
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select League", ["nba", "wnba"])
    st.divider()
    # Chat AI integration point
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        # Add your AI logic response here
        response = f"AI Analysis: Based on {league} trends, I see high variance in the market."
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)

# 4. Main Dashboard Fragment
@st.fragment(run_every=10)
def render_terminal():
    st.title(f"🏀 {league.upper()} Arbitrage Terminal")
    
    # [Insert your data fetching logic here]
    # Mock data for structure
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Live Score", "19 - 13", delta="Q1")
    with c2: st.metric("Mirror Projection", "64.0 pts")
    with c3: st.metric("Baseline", "41.5 pts")
    with c4: st.metric("Status", "VOLATILE")
    
    st.markdown("---")
    st.markdown("#### 📊 Multi-Platform Variance Matrix")
    df = pd.DataFrame([
        {"Platform": "📈 Polymarket", "Line": 40.5, "Var": 23.5, "Signal": "OVER"},
        {"Platform": "🏛️ Kalshi", "Line": 39.5, "Var": 24.5, "Signal": "OVER"}
    ])
    
    # Modern Table
    st.dataframe(
        df.style.map(lambda x: 'color: #00ff41; font-weight: bold;', subset=['Signal']),
        use_container_width=True, hide_index=True
    )

render_terminal()
