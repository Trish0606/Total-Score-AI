import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Frame Setup
st.set_page_config(page_title="Pure Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Math Assistant")
st.markdown("Automated live betting tracking engine utilizing your custom 80% quarter velocity rules.")

# 2. Controls
st.sidebar.header("🕹️ Engine Controls")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# Default constants
original_pts_per_min = 5.0
pts_per_min = 5.0 if league_choice == "nba" else 4.0
mirror_time = "6:00" if league_choice == "nba" else "5:00"

st.subheader(f"📡 Current Live {league_choice.upper()} Match Overview")

# 3. Modern Live Fragment Processing
# This decorator handles the loop automatically without crashing the system
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    live_games = fetch_live_scores(league_choice)

    if not live_games:
        st.info(f"✨ No active live {league_choice.upper()} data feeds detected. System idling until court clocks start.")
        return

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
        
        t1_q_scores = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q_scores = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        
        q1_total = (t1_q_scores[0] + t2_q_scores[0]) if len(t1_q_scores) >= 1 else 0
        q_total = (t1_q_scores[quarter-1] + t2_q_scores[quarter-1]) if (len(t1_q_scores) >= quarter) else 0

        try:
            mins, secs = map(int, clock.split(":"))
            time_left = mins + (secs / 60.0)
        except ValueError:
            time_left = 0.0

        adjusted_pacing = q_total + (time_left * pts_per_min)
        mirror_pred = q_total * 2
        
        with st.container():
            st.write("---")
            st.markdown(f"### ⚔️ {game_name} | Running Clock: `Q{quarter} - {clock}`")
            v1, v2 = st.columns(2)
            with v1:
                st.markdown("#### 📍 CURRENT COURT REALITY")
                st.write(f"• **Game Total:** `{game_total}` | **Q{quarter} Total:** `{q_total}`")
                st.info(f"**Velocity Projection:** {round(adjusted_pacing, 1)} pts")
            with v2:
                st.markdown("#### 🧠 MIRROR TRIGGER")
                st.write(f"• **2x Anchor:** {mirror_pred}.0 pts")

# 4. Deployment
render_live_dashboard()
