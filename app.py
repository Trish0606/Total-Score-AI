import streamlit as st
from src.ingestion import fetch_live_scores

# 1. Page Configuration
st.set_page_config(page_title="Math AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

# 2. Controls
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# 3. Data Rendering Fragment
@st.fragment(run_every=refresh_rate)
def render_live_dashboard():
    # Setup constants
    if league_choice == "nba":
        pts_per_min, base_line = 5.0, 55.5
    else:
        pts_per_min, base_line = 4.0, 41.5

    live_games = fetch_live_scores(league_choice)
    if not live_games:
        st.info("Waiting for tip-off...")
        return

    for game in live_games:
        # Data Extraction
        comp = game.get("competitions", [{}])[0]
        status = comp.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
        
        t1_q = [int(q.get("value", 0)) for q in comp["competitors"][0].get("linescores", [])]
        t2_q = [int(q.get("value", 0)) for q in comp["competitors"][1].get("linescores", [])]
        
        quarter = status.get("period", 1)
        q_total = (t1_q[quarter-1] + t2_q[quarter-1]) if len(t1_q) >= quarter else 0
        game_total = sum(t1_q) + sum(t2_q)
        mirror_pred = q_total * 2
        fh_proj = (sum(t1_q[:2]) + sum(t2_q[:2])) if len(t1_q) >= 2 else (q_total * 2)

        st.write("---")
        st.markdown(f"### ⚔️ {game.get('name')} | `Q{quarter}` | 🕒 `{status.get('displayClock')}`")

        # --- THE TOP PART (Macro & Active Analytics) ---
        st.markdown("##### 🎯 Active Quarter & Macro Analytics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Live Score (Total)", game_total, f"Q{quarter}: {q_total} pts")
        col2.metric("Mirror Projection", f"{mirror_pred:.1f} pts")
        col3.metric("1H Projection", f"{fh_proj:.1f} pts")
        col4.metric("Standard Baseline", f"{base_line} pts")

        # --- THE VARIANCE MATRIX ---
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        platforms = [
            {"Platform": "📡 ESPN Feed Data", "Mech": "Active Court Reality", "Line": f"{q_total} pts", "Var": "— (Anchor)"},
            {"Platform": "📈 Polymarket Link", "Mech": "Peer-to-Peer", "Line": f"O/U {base_line - 1.0}", "Var": f"{mirror_pred - (base_line-1.0):.1f} pts"},
            {"Platform": "👑 DraftKings Link", "Mech": "House Line", "Line": f"O/U {base_line}", "Var": f"{mirror_pred - base_line:.1f} pts"}
        ]
        st.table(platforms)

render_live_dashboard()
