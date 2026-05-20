import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Configuration
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

# 2. Controls
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # League Constants
    if league_choice == "nba":
        pts_per_min, mirror_time, base_line = 5.0, "6:00", 55.5
    else:
        pts_per_min, mirror_time, base_line = 4.0, "5:00", 41.5

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info(f"✨ No live {league_choice.upper()} games detected. Waiting for tip-off...")
        return

    for game in live_games:
        # --- Data Extraction ---
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
        
        mirror_pred = q_total * 2
        
        # --- UI Display ---
        st.write("---")
        st.markdown(f"### ⚔️ {game_name} | `Q{quarter}` | 🕒 Clock: `{clock}`")
        
        # Row 1: Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Live Scoreboard", f"{t1_score} - {t2_score}", f"Q{quarter}: {q_total} pts")
        m2.metric("Mirror Projection", f"{mirror_pred}.0 pts")
        m3.metric("Standard House Baseline", f"{base_line} pts")
        
        # --- ROW 3: VARIANCE ARBITRAGE TABLE (Matching your image) ---
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        # Calculating variances to match your screenshot
        poly_var = mirror_pred - (base_line - 1.0)
        dk_var = mirror_pred - base_line
        
        comparison_data = [
            {"Platform": "📡 ESPN Feed Data", "Market Mechanism": "Active Court Reality", "Line / Price Target": f"{q_total} Points", "Variance vs. Engine": "— (Anchor)"},
            {"Platform": "📈 Polymarket Link", "Market Mechanism": "Peer-to-Peer Contracts", "Line / Price Target": f"O/U {base_line - 1.0} (54¢)", "Variance vs. Engine": f"{round(poly_var, 1)} pts"},
            {"Platform": "👑 DraftKings Link", "Market Mechanism": "Traditional House Line", "Line / Price Target": f"{base_line} Total O/U", "Variance vs. Engine": f"{round(dk_var, 1)} pts"}
        ]
        
        st.table(comparison_data)

render_live_dashboard()
