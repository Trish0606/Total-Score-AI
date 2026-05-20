import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Configuration
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

# 2. Sidebar
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # League Constants
    if league_choice == "nba":
        pts_per_min, mirror_time = 5.0, "6:00"
    else:
        pts_per_min, mirror_time = 4.0, "5:00"

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info("✨ No live games detected. Waiting for tip-off...")
        return

    for game in live_games:
        # Data Extraction
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
            
        game_name = game.get("name")
        clock = status.get("displayClock", "0:00")
        quarter = status.get("period", 1)
        competitors = competition.get("competitors", [])
        
        # Calculate Q_Total
        t1_q = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        q_total = (t1_q[quarter-1] + t2_q[quarter-1]) if len(t1_q) >= quarter else 0
        
        # Engine Math
        mirror_pred = q_total * 2
        
        # --- FIXED INDENTATION FOR MARKET LINES ---
        market_lines = {
            "📈 Polymarket": 40.5, 
            "🏛️ Kalshi": 39.5, 
            "👑 DraftKings": 41.5
        }
        
        def get_signal(var):
            if var > 1.5: return "📈 OVER"
            if var < -1.5: return "📉 UNDER"
            return "➖ NEUTRAL"

        st.write("---")
        st.markdown(f"### ⚔️ {game_name} | `Q{quarter}` | 🕒 Clock: `{clock}`")
        
        # Variance Matrix
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        comparison_data = []
        for platform, market_total in market_lines.items():
            variance = mirror_pred - market_total
            comparison_data.append({
                "Platform": platform,
                "Live Market Total": market_total,
                "Engine Projection": f"{mirror_pred:.1f}",
                "Variance": f"{variance:.1f}",
                "Signal": get_signal(variance)
            })
            
        st.table(comparison_data)

render_live_dashboard()
