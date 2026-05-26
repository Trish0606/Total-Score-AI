import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores

# 1. Advanced Custom Styling
st.set_page_config(page_title="Arbitrage AI Core", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #0e1117; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .css-1r6slp0 { padding: 1rem; }
    h5 { color: #80848e; text-transform: uppercase; letter-spacing: 1px; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏀 Total Score AI Arbitrage Terminal")

@st.fragment(run_every=10)
def render_live_dashboard():
    # --- DATA LOGIC (Simplified for logic clarity) ---
    mirror_pred = 64.0  # Simulated projection
    base_line = 41.5
    
    # --- TOP ANALYTICS ROW ---
    st.markdown("##### 🎯 Active Quarter Analytics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Score", "19 - 13", delta="Q1: 32 pts")
    c2.metric("Mirror Projection", f"{mirror_pred} pts")
    c3.metric("Baseline", f"{base_line} pts")
    c4.metric("Market Status", "HIGH VOLATILITY")

    # --- ADVANCED VARIANCE MATRIX ---
    st.markdown("#### 📊 Multi-Platform Variance Matrix")
    
    df = pd.DataFrame([
        {"Platform": "📈 Polymarket", "Line": 40.5, "Var": 23.5, "Signal": "OVER"},
        {"Platform": "🏛️ Kalshi", "Line": 39.5, "Var": 24.5, "Signal": "OVER"},
        {"Platform": "👑 DraftKings", "Line": 41.5, "Var": 22.5, "Signal": "OVER"}
    ])

    # Apply conditional formatting to the table
    st.dataframe(
        df.style.applymap(lambda x: 'color: #00ff41; font-weight: bold;', subset=['Signal']),
        use_container_width=True,
        hide_index=True
    )

render_live_dashboard()
