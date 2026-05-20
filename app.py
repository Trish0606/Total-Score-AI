import streamlit as st
from src.ingestion import fetch_live_scores

st.set_page_config(page_title="Math AI Engine", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")

@st.fragment(run_every=30)
def render_live_dashboard():
    league_choice = st.sidebar.selectbox("Select League", ["nba", "wnba"])
    live_games = fetch_live_scores(league_choice)

    if not live_games:
        st.info("Waiting for tip-off...")
        return

    for game in live_games:
        # Data Extraction
        comp = game.get("competitions", [{}])[0]
        status = comp.get("status", {})
        if status.get("type", {}).get("state") != "in": continue
            
        # Stats
        t1_q = [int(q.get("value", 0)) for q in comp["competitors"][0].get("linescores", [])]
        t2_q = [int(q.get("value", 0)) for q in comp["competitors"][1].get("linescores", [])]
        
        quarter = status.get("period", 1)
        q_total = (t1_q[quarter-1] + t2_q[quarter-1]) if len(t1_q) >= quarter else 0
        game_total = sum(t1_q) + sum(t2_q)
        
        # Projections
        mirror_pred = q_total * 2
        # First Half Projection (Calculated immediately based on current rate)
        fh_proj = (sum(t1_q[:2]) + sum(t2_q[:2])) if len(t1_q) >= 2 else (q_total * 2)

        st.write("---")
        st.markdown(f"### ⚔️ {game.get('name')} | `Q{quarter}` | `{status.get('displayClock')}`")

        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Live Total (Game)", game_total)
        m2.metric("Live Quarter Total", q_total)
        m3.metric("Mirror Projection", f"{mirror_pred:.1f}")
        m4.metric("1H Projection", f"{fh_proj:.1f}")

        # Variance Table
        st.markdown("#### 📊 Multi-Platform Variance Matrix")
        
        # Platform Data: Line (Total) | Odds (Live)
        platforms = {
            "📈 Polymarket": {"total": 53.5, "odds": "-110"},
            "🏛️ Kalshi": {"total": 54.0, "odds": "-105"},
            "👑 DraftKings": {"total": 54.5, "odds": "-115"}
        }

        comparison_data = []
        for name, data in platforms.items():
            var = mirror_pred - data['total']
            comparison_data.append({
                "Platform": name,
                "Live Market Total": data['total'],
                "Live Odds": data['odds'],
                "Variance": f"{var:.1f}",
                "Signal": "📈 OVER" if var > 1.5 else ("📉 UNDER" if var < -1.5 else "➖")
            })
        st.table(comparison_data)

render_live_dashboard()
