import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores

# 1. Page & Modern Terminal Styling
st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")
st.markdown("""
    <style>
    /* Dark mode terminal cards */
    div[data-testid="stMetric"] {
        background-color: #0e1117;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    h4, h5 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏀 Total Score AI Arbitrage Terminal")

@st.fragment(run_every=10)
def render_live_dashboard():
    # --- DATA ENGINE (Logic Layer) ---
    # Replace with your actual data fetching logic
    df = pd.DataFrame([
        {"Platform": "📈 Polymarket", "Line": 40.5, "Var": 23.5, "Signal": "OVER"},
        {"Platform": "🏛️ Kalshi", "Line": 39.5, "Var": 24.5, "Signal": "OVER"},
        {"Platform": "👑 DraftKings", "Line": 41.5, "Var": 22.5, "Signal": "OVER"}
    ])

    # --- TOP METRICS ---
    st.markdown("##### 🎯 Active Quarter Analytics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Score", "19 - 13", delta="Q1: 32 pts")
    c2.metric("Mirror Projection", "64.0 pts")
    c3.metric("Baseline", "41.5 pts")
    c4.metric("Market Status", "VOLATILE")

    # --- ADVANCED VARIANCE MATRIX ---
    st.markdown("#### 📊 Multi-Platform Variance Matrix")
    
    # Use .map() instead of .applymap() to fix your AttributeError
    styled_df = df.style.map(
        lambda x: 'color: #00ff41; font-weight: bold;' if x == "OVER" else '', 
        subset=['Signal']
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )

render_live_dashboard()
