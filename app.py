import streamlit as st
import time
from src.ingestion import fetch_live_scores
from src.features import calculate_betting_advantage

# 1. Setup Browser Page Configuration
st.set_page_config(
    page_title="Total Score AI Assistant",
    page_icon="🏀",
    layout="wide"
)

st.title("🏀 Total Score AI Math Assistant")
st.markdown("Automated live betting tracking engine utilizing your custom 80% quarter velocity rules.")

# 2. Sidebar Controls
st.sidebar.header("🕹️ Engine Controls")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# Simulate automatic rerun loop for real-time live data
st.sidebar.markdown(f"⏱️ Next data update in {refresh_rate}s...")

# 3. Main Data Core Execution
st.subheader(f"📡 Current Live {league_choice.upper()} Match Overview")

live_games = fetch_live_scores(league_choice)

if not live_games:
    st.info(f"✨ There are no active live {league_choice.upper()} games right now. The engine is idling until game time.")
else:
    # Build columns or cards for each active game found
    for game in live_games:
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        
        # We only care about live active games
        if status.get("type", {}).get("state") != "in":
            continue
            
        game_name = game.get("name")
        clock = status.get("displayClock", "0:00")
        quarter = status.get("period", 1)
        
        # Total scores
        competitors = competition.get("competitors", [])
        t1_name = competitors[0].get("team", {}).get("shortDisplayName", "Team 1")
        t2_name = competitors[1].get("team", {}).get("shortDisplayName", "Team 2")
        t1_score = int(competitors[0].get("score", 0))
        t2_score = int(competitors[1].get("score", 0))
        game_total = t1_score + t2_score
        
        # Quarter scores
        t1_q_scores = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q_scores = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        q_total = (t1_q_scores[quarter-1] + t2_q_scores[quarter-1]) if (len(t1_q_scores) >= quarter) else 0

        # Build a beautiful visual UI container card for this specific game
        with st.container():
            st.write("---")
            col1, col2, col3 = st.columns([2, 2, 3])
            
            with col1:
                st.markdown(f"### ⚔️ {game_name}")
                st.markdown(f"**⏱️ Period:** Q{quarter} | **🕒 Clock:** `{clock}`")
                st.metric(label="Live Game Total Score", value=f"{game_total} pts")
                
            with col2:
                st.markdown("##### 📊 Live Scoreboard")
                st.write(f"🔹 {t1_name}: **{t1_score}**")
                st.write(f"🔹 {t2_name}: **{t2_score}**")
                st.write(f"📍 Current Q{quarter} Total: **{q_total}**")
                
            with col3:
                st.markdown("##### 🎯 AI Mathematical Edge Engine")
                
                # Check for Rule 1: The 6-Minute Mirror
                if clock == "6:00":
                    mirror_pred = q_total * 2
                    st.warning(f"🚨 **6-Min Trigger Hit!** Projected Quarter Total: **{mirror_pred}**")
                    alert = calculate_betting_advantage(mirror_pred, 55.5, threshold=3.5)
                    st.code(alert, language="text")
                
                # Rule 2: Constant Velocity pacing calculation
                try:
                    mins, secs = map(int, clock.split(":"))
                    time_left = mins + (secs / 60.0)
                    pacing_pred = q_total + (time_left * 5)
                    st.info(f"📈 **Pacing Velocity Estimate:** Quarter score heading toward: **{round(pacing_pred, 1)}** pts.")
                except ValueError:
                    pass

# Force page reload based on user's slider setting
time.sleep(refresh_rate)
st.rerun()
