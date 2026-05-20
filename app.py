import streamlit as st
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
        pts_per_min, base_line, mirror_time = 5.0, 55.5, "6:00"
    else:
        pts_per_min, base_line, mirror_time = 4.0, 41.5, "5:00"

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info("Waiting for tip-off...")
        return

    for game in live_games:
        # Data Extraction
        comp = game.get("competitions", [{}])[0]
        status = comp.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
        
        # Scoring
        t1_score = int(comp["competitors"][0].get("score", 0))
        t2_score = int(comp["competitors"][1].get("score", 0))
        t1_q = [int(q.get("value", 0)) for q in comp["competitors"][0].get("linescores", [])]
        t2_q = [int(q.get("value", 0)) for q in comp["competitors"][1].get("linescores", [])]
        
        q_idx = status.get("period", 1) - 1
        q_total = (t1_q[q_idx] + t2_q[q_idx])
        game_total = sum(t1_q) + sum(t2_q)
        
        # Calculations
        mirror_pred = q_total * 2
        fh_actual = sum(t1_q[:2]) + sum(t2_q[:2])
        fh_proj = fh_actual if q_idx >= 1 else (q_total * 2)

        st.write("---")
        st.markdown(f"### ⚔️ {game.get('name')} | `Q{status.get('period')}` | 🕒 `{status.get('displayClock')}`")

        # --- ROW 1: Active Quarter Analytics ---
        st.markdown("##### 🎯 Active Quarter Analytics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Live Scoreboard", f"{t1_score} - {t2_score}", delta=f"Q{status.get('period')}: {q_total} pts")
        m2.metric("Target Adjusted Pacing", f"{q_total*1.5:.1f} pts", delta=f"Using {pts_per_min} PPM matrix")
        m3.metric("Midpoint Mirror Target", f"{mirror_pred:.1f} pts", delta=f"Triggers @ {mirror_time}")
        m4.metric("Standard House Baseline", f"{base_line} pts")

        # --- ROW 2: Macro Game-Flow ---
        st.markdown("##### 🧠 Macro Game-Flow Guide")
        g1, g2, g3, g4 = st.columns(4)
        g1.metric("1st Half Projection Anchor", "Waiting for Q2..." if q_idx == 0 else f"{fh_proj:.1f} pts")
        g2.metric("1st Half Score Actual", f"{fh_actual} pts", delta="Waiting for Q1 buzzer" if q_idx == 0 else None)
        g3.metric("Full Game Projection (1Hx2)", "Waiting for Q4..." if q_idx < 3 else f"{fh_actual*2:.1f} pts")
        g4.metric("Current Running Game Total", f"{game_total} pts", delta="Through Q" + str(status.get('period')))

        # --- ROW 3: Variance Matrix ---
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        platforms = [
            {"Platform": "📡 ESPN Feed Data", "Mech": "Active Court Reality", "Line": f"{q_total} Points", "Var": "— (Anchor)"},
            {"Platform": "📈 Polymarket Link", "Mech": "Peer-to-Peer Contracts", "Line": f"O/U {base_line - 1.0} (54¢)", "Var": f"{mirror_pred - (base_line-1.0):.1f} pts"},
            {"Platform": "👑 DraftKings Link", "Mech": "Traditional House Line", "Line": f"{base_line} Total O/U", "Var": f"{mirror_pred - base_line:.1f} pts"}
        ]
        
        # Display the table
        import pandas as pd
        st.table(pd.DataFrame(platforms))

render_live_dashboard()
