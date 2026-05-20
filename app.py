import streamlit as st
import time
from src.ingestion import fetch_live_scores

# 1. Page Frame Setup
st.set_page_config(page_title="Pure Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Math Assistant")
st.markdown("Automated live betting tracking engine utilizing your custom 80% quarter velocity rules.")

# 2. Controls
st.sidebar.header("🕹️ Engine Controls")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# Default historical constants
original_pts_per_min = 5.0

if league_choice == "nba":
    pts_per_min = 5.0
    mirror_time = "6:00"
else:
    pts_per_min = 4.0
    mirror_time = "5:00"

st.subheader(f"📡 Current Live {league_choice.upper()} Match Overview")
live_games = fetch_live_scores(league_choice)

if not live_games:
    st.info(f"✨ No active live {league_choice.upper()} data feeds detected. System idling until court clocks start.")
else:
    for game in live_games:
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        
        if status.get("type", {}).get("state") != "in":
            continue
            
        game_name = game.get("name")
        clock = status.get("displayClock", "0:00")
        quarter = status.get("period", 1)
        
        competitors = competition.get("competitors", [])
        t1_score = int(competitors[0].get("score", 0))
        t2_score = int(competitors[1].get("score", 0))
        game_total = t1_score + t2_score
        
        # Quarter score arrays from ESPN Core data
        t1_q_scores = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q_scores = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        
        q1_total = (t1_q_scores[0] + t2_q_scores[0]) if len(t1_q_scores) >= 1 else 0
        q2_total = (t1_q_scores[1] + t2_q_scores[1]) if len(t1_q_scores) >= 2 else 0
        q3_total = (t1_q_scores[2] + t2_q_scores[2]) if len(t1_q_scores) >= 3 else 0
        q4_total = (t1_q_scores[3] + t2_q_scores[3]) if len(t1_q_scores) >= 4 else 0
        
        first_half_actual = q1_total + q2_total
        q_total = (t1_q_scores[quarter-1] + t2_q_scores[quarter-1]) if (len(t1_q_scores) >= quarter) else 0

        try:
            mins, secs = map(int, clock.split(":"))
            time_left = mins + (secs / 60.0)
        except ValueError:
            time_left = 0.0

        # Mathematical Execution Core
        adjusted_pacing = q_total + (time_left * pts_per_min)
        original_pacing = q_total + (time_left * original_pts_per_min)
        mirror_pred = q_total * 2
        
        with st.container():
            st.write("---")
            st.markdown(f"### ⚔️ {game_name} | Running Clock: `Q{quarter} - {clock}`")
            
            v_col1, v_col2 = st.columns(2)
            
            with v_col1:
                st.markdown("#### 📍 CURRENT COURT REALITY")
                st.write(f"• **Cumulative Game Score:** `{game_total} Points`")
                st.write(f"• **Active Q{quarter} Score Baseline:** `{q_total} Points`")
                
                st.markdown("#### 📈 MICRO-QUARTER PROJECTIONS")
                st.info(f"**Adjusted Velocity Matrix ({int(pts_per_min)} PTS/MIN):**\n\nQuarter expected finish: **{round(adjusted_pacing, 1)} Points**")
                st.write(f"**Original Anchor Matrix (5 PTS/MIN):**\n\nQuarter expected finish: **{round(original_pacing, 1)} Points**")
                
                if clock == mirror_time:
                    st.success(f"🚨 **MIDPOINT MIRROR TRIGGER HIT ({mirror_time}):**\n\nPure 2x Score Prediction: **{mirror_pred}.0 Points**")
                else:
                    st.write(f"**Midpoint Mirror (2x Anchor):** Predicts **{mirror_pred}.0 Points** *(Locks at exactly {mirror_time})*")
                    
            with v_col2:
                st.markdown("#### 🧠 MACRO GAME-FLOW PROJECTIONS")
                
                # First Half Prediction Stack
                if quarter == 1:
                    st.write("• **1st Half Prediction (Q1 × 2):** `Waiting for Q2...`")
                    st.write(f"• **1st Half Cumulative Points:** `{game_total} pts (Q1 Live)`")
                else:
                    st.write(f"• **1st Half Prediction (Q1 × 2):** **{q1_total * 2}.0 Points**")
                    st.write(f"• **1st Half Cumulative Points:** `{first_half_actual} pts` *(Q1: {q1_total} | Q2: {q2_total})*")
                
                st.write("---")
                
                # Full Game Prediction Stack
                if quarter < 4:
                    st.write("• **Full Game Prediction (1H × 2):** `Waiting for Q4...`")
                    st.write(f"• **Current Total Accumulation:** `{game_total} Points`")
                else:
                    st.write(f"• **Full Game Prediction (1H × 2 Anchor):** **{first_half_actual * 2}.0 Points**")
                    st.write(f"• **Current Total Accumulation:** `{game_total} Points (Q4 Live)`")

# 3. Safe Auto-Refresh Execution Loop
time.sleep(refresh_rate)
st.experimental_rerun()
