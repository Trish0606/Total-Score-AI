import streamlit as st
import pandas as pd
from src.ingestion import fetch_live_scores

st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

# Sidebar
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # Constants
    pts_per_min = 5.0 if league_choice == "nba" else 4.0
    base_line = 55.5 if league_choice == "nba" else 41.5

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info("Waiting for tip-off...")
        return

    for game in live_games:
        comp = game.get("competitions", [{}])[0]
        status = comp.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
        
        # Scoring Logic
        t1_q = [int(q.get("value", 0)) for q in comp["competitors"][0].get("linescores", [])]
        t2_q = [int(q.get("value", 0)) for q in comp["competitors"][1].get("linescores", [])]
        q_idx = status.get("period", 1) - 1
        q_total = (t1_q[q_idx] + t2_q[q_idx])
        game_total = sum(t1_q) + sum(t2_q)
        
        # Projections
        mirror_pred = q_total * 2
        fh_actual = sum(t1_q[:2]) + sum(t2_q[:2])
        fh_proj = fh_actual if q_idx >= 1 else (q_total * 2)

        st.write("---")
        st.markdown(f"### ⚔️ {game.get('name')} | `Q{status.get('period')}` | 🕒 `{status.get('displayClock')}`")

        # Row 1: Active Quarter Analytics (Now includes Live Total/Quarter)
        st.markdown("##### 🎯 Active Quarter Analytics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Live Quarter Total", f"{q_total} pts", delta=f"Current Q{status.get('period')}")
        m2.metric("Current Running Game Total", f"{game_total} pts", delta="Total Points Scored")
        m3.metric("Mirror Projection", f"{mirror_pred:.1f} pts", delta="Engine Prediction")
        m4.metric("Target Adjusted Pacing", f"{q_total*1.5:.1f} pts")

        # Row 2: Macro Analytics
        st.markdown("##### 🧠 Macro Game-Flow Guide")
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("1st Half Projection", f"{fh_proj:.1f} pts")
        g2.metric("1st Half Score Actual", f"{fh_actual} pts")
        g3.metric("Full Game Projection (1Hx2)", f"{fh_actual*2:.1f} pts")
        g4.metric("Standard House Baseline", f"{base_line} pts")

        # Row 3: Variance Matrix
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        platforms = {
            "📈 Polymarket": {"total": 40.5, "odds": "(54¢)"},
            "🏛️ Kalshi": {"total": 39.5, "odds": "(60¢)"},
            "👑 DraftKings": {"total": 41.5, "odds": ""}
        }

        data = []
        for name, val in platforms.items():
            var = mirror_pred - val['total']
            data.append({
                "Platform": name,
                "Line / Price Target": f"O/U {val['total']} {val['odds']}",
                "Variance vs. Engine": f"{var:.1f} pts",
                "Signal": "📈 OVER" if var > 1.5 else ("📉 UNDER" if var < -1.5 else "➖ NEUTRAL")
            })
        st.table(pd.DataFrame(data))

render_live_dashboard()
