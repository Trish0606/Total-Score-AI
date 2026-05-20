import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Configuration
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")
st.markdown("Comparing custom league-specific pacing against macro game-total models and live prediction markets.")

# 2. Sidebar Controls
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

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
        
        # Engine Calculations
        mirror_pred = q_total * 2
        
        # --- UI LAYOUT ---
        st.write("---")
        st.markdown(f"### ⚔️ {game_name} | `Q{quarter}` | 🕒 Clock: `{clock}`")
        
        # Metrics Row
        m1, m2, m3 = st.columns(3)
        m1.metric("Live Scoreboard", f"{t1_score} - {t2_score}", f"Q{quarter}: {q_total} pts")
        m2.metric("Mirror Projection", f"{mirror_pred:.1f} pts")
        m3.metric("Standard House Baseline", "41.5 pts") # Example baseline
        
        # Variance Matrix
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        # Live Market Lines
        market_lines = {
            "📈 Polymarket Link": {"mech": "Peer-to-Peer", "line": 40.5, "price": "(54¢)"},
            "🏛️ Kalshi Link": {"mech": "Regulated Financials", "line": 39.5, "price": "(60¢)"},
            "👑 DraftKings Link": {"mech": "Traditional House Line", "line": 41.5, "price": ""}
        }
        
        def get_signal(var):
            if var > 1.5: return "📈 OVER"
            if var < -1.5: return "📉 UNDER"
            return "➖ NEUTRAL"

        comparison_data = [
            {"Platform": "📡 ESPN Feed Data", "Market Mechanism": "Active Court Reality", "Line / Price Target": f"{q_total} Points", "Variance vs. Engine": "— (Anchor)", "Signal": ""}
        ]
        
        for name, data in market_lines.items():
            var = mirror_pred - data['line']
            comparison_data.append({
                "Platform": name,
                "Market Mechanism": data['mech'],
                "Line / Price Target": f"O/U {data['line']} {data['price']}",
                "Variance vs. Engine": f"{var:.1f} pts",
                "Signal": get_signal(var)
            })
            
        st.table(comparison_data)

render_live_dashboard()
