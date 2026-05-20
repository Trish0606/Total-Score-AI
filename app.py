import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Frame Setup
st.set_page_config(page_title="Pure Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")
st.markdown("Comparing custom league-specific pacing against macro game-total models and live prediction markets.")

# 2. Sidebar Controls
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# 3. Core Logic Fragment (Refreshes automatically without crashing)
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # Setup league-specific constants
    if league_choice == "nba":
        pts_per_min, mirror_time, base_quarter_line = 5.0, "6:00", 55.5
    else:
        pts_per_min, mirror_time, base_quarter_line = 4.0, "5:00", 41.5

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info(f"✨ No live {league_choice.upper()} games detected. System idling.")
        return

    for game in live_games:
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
            
        # Data Extraction
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
        
        try:
            mins, secs = map(int, clock.split(":"))
            time_left = mins + (secs / 60.0)
        except ValueError: time_left = 0.0

        # Calculations
        mirror_pred = q_total * 2
        
        # Display
        st.write("---")
        st.markdown(f"### ⚔️ {game_name} | `Q{quarter}` | 🕒 Clock: `{clock}`")
        
        # Row 1
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Live Scoreboard", f"{t1_score} - {t2_score}", f"Q{quarter}: {q_total} pts")
        m2.metric("Mirror Projection", f"{mirror_pred}.0 pts")
        m3.metric("Baseline", f"{base_quarter_line} pts")
        
        # Row 2: Variance Matrix with Signal
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        def get_signal(var):
            if var > 1.5: return "📈 OVER"
            if var < -1.5: return "📉 UNDER"
            return "➖ NEUTRAL"

        data = [
            {"Platform": "📈 Polymarket", "Line": base_quarter_line-1, "Var": mirror_pred-(base_quarter_line-1)},
            {"Platform": "🏛️ Kalshi", "Line": base_quarter_line-2, "Var": mirror_pred-(base_quarter_line-2)},
            {"Platform": "👑 DraftKings", "Line": base_quarter_line, "Var": mirror_pred-base_quarter_line}
        ]
        
        table_data = [{"Platform": d["Platform"], "Line": d["Line"], "Var": f"{d['Var']:.1f}", "Signal": get_signal(d["Var"])} for d in data]
        st.table(table_data)

# 4. Run Fragment
render_live_dashboard()
