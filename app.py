import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Configuration
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

# 2. Sidebar Controls
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# 3. Core Logic Fragment
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # Setup league constants
    if league_choice == "nba":
        pts_per_min, mirror_time = 5.0, "6:00"
    else:
        pts_per_min, mirror_time = 4.0, "5:00"

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info(f"✨ No live {league_choice.upper()} games detected. Waiting for tip-off...")
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
        t1_score = int(competitors[0].get("score", 0))
        t2_score = int(competitors[1].get("score", 0))
        game_total = t1_score + t2_score
        
        t1_q = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        q_total = (t1_q[quarter-1] + t2_q[quarter-1]) if len(t1_q) >= quarter else 0
        
        # Engine Math
        mirror_pred = q_total * 2
        
        # Display
        st.write("---")
        st.markdown(f"### ⚔️ {game_name} | `Q{quarter}` | 🕒 Clock: `{clock}`")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Live Scoreboard", f"{t1_score} - {t2_score}", f"Q{quarter}: {q_total} pts")
        m2.metric("Engine Projection", f"{mirror_pred:.1f} pts")
        
        # Variance Matrix
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        # Placeholder market totals (Replace these with your 'fetch_' functions)
        market_lines = {
            "📈 Polymarket": 53.5, 
            "🏛️ Kalshi": 54.0, 
            "👑 DraftKings": 54.5
        }
        
        def get_signal(var):
            if var > 1.5: return "📈 OVER"
            if var < -1.5: return "📉 UNDER"
            return "➖ NEUTRAL"

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

# 4. Run Fragment
render_live_dashboard()
