import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Configuration
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Math Assistant")
st.markdown("Automated Variance Matrix: Tracking ESPN against Market Lines.")

# 2. Controls
league_choice = st.sidebar.selectbox("Select League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh (seconds)", 10, 60, 30)

# 3. Modern Live Fragment Processing
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    live_games = fetch_live_scores(league_choice)

    if not live_games:
        st.info("✨ No active games. Waiting for tip-off...")
        return

    for game in live_games:
        # Basic Game Data Extraction
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
            
        game_name = game.get("name")
        clock = status.get("displayClock", "0:00")
        
        # Calculate Engine Total (Mock logic - replace with your specific math)
        # You can add inputs for the external market lines here
        engine_total = 52.0  # Placeholder for your engine's projection
        
        st.write("---")
        st.markdown(f"### ⚔️ {game_name} | {clock}")
        
        # 📊 Variance Matrix Display
        st.markdown("### 📊 MULTI-PLATFORM VARIANCE MATRIX")
        
        # Example values (You would replace these with dynamic inputs or data fetches)
        pk_line = 54.5
        kl_line = 53.5
        dk_line = 55.5
        
        data = {
            "Platform": ["Polymarket", "Kalshi", "DraftKings"],
            "Live Line": [pk_line, kl_line, dk_line],
            "Variance vs Engine": [f"{engine_total - pk_line:.1f}", 
                                   f"{engine_total - kl_line:.1f}", 
                                   f"{engine_total - dk_line:.1f}"]
        }
        st.table(data)

# 4. Run the dashboard
render_live_dashboard()
