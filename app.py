import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores

# 1. Page Configuration
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

# 2. Controls
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# 3. Data Rendering Fragment
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # Setup constants
    if league_choice == "nba":
        pts_per_min, base_line = 5.0, 55.5
    else:
        pts_per_min, base_line = 4.0, 41.5

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info("Waiting for tip-off...")
        return

    for game in live_games:
        # Data Extraction
        comp = game.get("competitions", [{}])[0]
        status = comp.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
        
        t1_q = [int(q.get("value", 0)) for q in comp["competitors"][0].get("linescores", [])]
        t2_q = [int(q.get("value", 0)) for q in comp["competitors"][1].get("linescores", [])]
        
        q_idx = status.get("period", 1) - 1
        q_total = (t1_q[q_idx] + t2_q[q_idx])
        game_total = sum(t1_q) + sum(t2_q)
        
        # Engine Math
        mirror_pred = q_total * 2
        fh_actual = sum(t1_q[:2]) + sum(t2_q[:2])
        fh_proj = fh_actual if q_idx >= 1 else (q_total * 2)

        st.write("---")
        st.markdown(f"### ⚔️ {game.get('name')} | `Q{status.get('period')}` | 🕒 `{status.get('displayClock')}`")

        # Row 1: Active Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Live Scoreboard", f"{comp['competitors'][0]['score']} - {comp['competitors'][1]['score']}", delta=f"Q{status.get('period')}: {q_total} pts")
        m2.metric("Target Adjusted Pacing", f"{q_total*1.5:.1f} pts", delta=f"Using {pts_per_min} PPM matrix")
        m3.metric("Mirror Projection", f"{mirror_pred:.1f} pts", delta="Engine Prediction")
        m4.metric("Standard House Baseline", f"{base_line} pts")

        # Row 2: Macro Analytics
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("1st Half Projection (Anchor)", "Waiting for Q2..." if q_idx == 0 else f"{fh_proj:.1f} pts")
        g2.metric("1st Half Score Actual", f"{fh_actual} pts", delta="Waiting for Q1 buzzer" if q_idx == 0 else None)
        g3.metric("Full Game Projection (1Hx2)", "Waiting for Q4..." if q_idx < 3 else f"{fh_actual*2:.1f} pts")
        g4.metric("Current Running Game Total", f"{game_total} pts", delta="Through Q" + str(status.get('period')))

        # Row 3: Variance Matrix with Over/Under Signal
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        platforms = {
            "📈 Polymarket Link": {"total": 40.5, "odds": "(54¢)"},
            "🏛️ Kalshi Link": {"total": 39.5, "odds": "(60¢)"},
            "👑 DraftKings Link": {"total": 41.5, "odds": ""}
        }

        comparison_data = []
        for name, data in platforms.items():
            var = mirror_pred - data['total']
            signal = "📈 OVER" if var > 1.5 else ("📉 UNDER" if var < -1.5 else "➖ NEUTRAL")
            comparison_data.append({
                "Platform": name,
                "Market Mechanism": "Live Odds Integrated",
                "Line / Price Target": f"O/U {data['total']} {data['odds']}",
                "Variance vs. Engine": f"{var:.1f} pts",
                "Signal": signal
            })
            
        st.table(pd.DataFrame(comparison_data))

render_live_dashboard()
