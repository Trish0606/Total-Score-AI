import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Frame Setup
st.set_page_config(page_title="Pure Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Math Assistant")
st.markdown("Automated live betting tracking engine.")

# 2. Controls
st.sidebar.header("🕹️ Engine Controls")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# 3. Modern Live Fragment Processing
# This handles refreshes automatically without crashing
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    st.subheader(f"📡 Current Live {league_choice.upper()} Match Overview")
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
        
        st.write("---")
        st.write(f"### ⚔️ {game_name}")
        st.write(f"**Status:** {clock} remaining in current period.")

# 4. Trigger
render_live_dashboard()
