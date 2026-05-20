import streamlit as st
from src.ingestion import fetch_live_scores

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

# 2. SIDEBAR CONTROLS (Must be outside the fragment)
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# 3. FRAGMENT (Contains only data rendering logic)
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # League Constants based on global 'league_choice'
    if league_choice == "nba":
        pts_per_min = 5.0
    else:
        pts_per_min = 4.0

    live_games = fetch_live_scores(league_choice)
    
    if not live_games:
        st.info(f"✨ No live {league_choice.upper()} games detected. Waiting for tip-off...")
        return
        
    for game in live_games:
        # Example: Render game data inside the fragment
        st.write("---")
        st.markdown(f"### ⚔️ {game.get('name')}")
        # Add your table logic and metric rows here...

# 4. CALL THE FRAGMENT
render_live_dashboard()
