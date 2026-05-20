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
        original_pacing = q_total + (time_left *
