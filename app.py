import streamlit as st
import pandas as pd

# 1. Define league-specific constants so they are always accurate
LEAGUE_PARAMS = {
    "nba": {"pace": 2.15, "baseline": 55.5},
    "wnba": {"pace": 1.95, "baseline": 41.5}
}

st.set_page_config(layout="wide")

# 2. Sidebar for League Selection
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    # Fetch parameters dynamically based on the selection
    params = LEAGUE_PARAMS[league]

# 3. Main Dashboard Layout
st.title(f"🏀 {league.upper()} Arbitrage Terminal")

# Use columns for a clean metric layout
c1, c2, c3, c4 = st.columns(4)

# Dynamic metrics using the params dictionary
c1.metric("Live Scoreboard", "53 - 37")
c2.metric("Live Market Line", f"{params['baseline']} pts")
c3.metric("Live Quarter Total", "42 pts")
c4.metric("Current Game Total", "90 pts")

# 4. Variance Matrix
st.markdown("#### 📊 Multi-Platform Variance Matrix")
data = [
    {"Platform": "Polymarket", "Line": 40.5, "Var": 23.5, "Signal": "OVER"},
    {"Platform": "DraftKings", "Line": 41.5, "Var": 22.5, "Signal": "OVER"}
]
# Use st.dataframe for reliable display without styling errors
st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
