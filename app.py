import streamlit as st
import time
from src.ingestion import fetch_live_scores
from src.features import calculate_betting_advantage

# 1. Page Frame Setup
st.set_page_config(page_title="Multi-Platform AI Engine", page_icon="🏀", layout="wide")
st.title("🏀 Total Score AI Platform Arbitrage Tracker")
st.markdown("Comparing custom league-specific pacing against macro game-total models and live prediction markets.")

# 2. Controls
st.sidebar.header("🕹️ Control Room")
league_choice = st.sidebar.selectbox("Select Target League", ["nba", "wnba"])
refresh_rate = st.sidebar.slider("Auto-Refresh Rate (seconds)", 10, 60, 30)

# Establish default anchor targets
original_pts_per_min = 5.0
original_base_line = 55.5

if league_choice == "nba":
    pts_per_min = 5.0
    mirror_time = "6:00"
    base_quarter_line = 55.5
else:
    pts_per_min = 4.0
    mirror_time = "5:00"
    base_quarter_line = 41.5

st.subheader(f"📡 Current Live {league_choice.upper()} Arbitrage Monitor")
live_games = fetch_live_scores(league_choice)

if not live_games:
    st.info(f"✨ No live {league_choice.upper()} games playing right now. System idling until game time.")
else:
    for game in live_games:
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        
        if status.get("type", {}).get("state") != "in":
            continue
            
        game_name = game.get("name")
        clock = status.get("displayClock", "0:00")
        quarter = status.get("period", 1)
        
        competitors = competition.get("competitors", [])
        t1_name = competitors[0].get("team", {}).get("shortDisplayName", "Team 1")
        t2_name = competitors[1].get("team", {}).get("shortDisplayName", "Team 2")
        t1_score = int(competitors[0].get("score", 0))
        t2_score = int(competitors[1].get("score", 0))
        game_total = t1_score + t2_score
        
        # Isolate individual quarterly line scores from ESPN API
        t1_q_scores = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q_scores = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        
        # Safe extraction helpers
        q1_total = (t1_q_scores[0] + t2_q_scores[0]) if len(t1_q_scores) >= 1 else 0
        q2_total = (t1_q_scores[1] + t2_q_scores[1]) if len(t1_q_scores) >= 2 else 0
        q3_total = (t1_q_scores[2] + t2_q_scores[2]) if len(t1_q_scores) >= 3 else 0
        q4_total = (t1_q_scores[3] + t2_q_scores[3]) if len(t1_q_scores) >= 4 else 0
        
        # Calculate active tracking variables
        first_half_actual = q1_total + q2_total
        q_total = (t1_q_scores[quarter-1] + t2_q_scores[quarter-1]) if (len(t1_q_scores) >= quarter) else 0

        try:
            mins, secs = map(int, clock.split(":"))
            time_left = mins + (secs / 60.0)
        except ValueError:
            time_left = 0.0

        # Core Mathematical Estimations
        adjusted_pacing = q_total + (time_left * pts_per_min)
        mirror_pred = q_total * 2
        
        with st.container():
            st.write("---")
            st.markdown(f"### ⚔️ {game_name} | `Q{quarter}` | 🕒 Clock: `{clock}`")
            
            # --- ROW 1: MICRO TARGET DECK (INDIVIDUAL QUARTERS) ---
            st.markdown("##### 🎯 Active Quarter Analytics")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Live Scoreboard", f"{t1_score} - {t2_score}", f"Q{quarter}: {q_total} pts")
            m2.metric("Target Adjusted Pacing", f"{round(adjusted_pacing, 1)} pts", f"Using {int(pts_per_min)} PPM matrix")
            m3.metric("Midpoint Mirror Target", f"{mirror_pred}.0 pts", f"Triggers @ {mirror_time}")
            m4.metric("Standard House Baseline", f"{base_quarter_line} pts")
            
            # --- ROW 2: MACRO TARGET DECK (HALF GAME & FULL GAME SWEATS) ---
            st.markdown("##### 🧠 Macro Game-Flow Guide")
            g1, g2, g3, g4 = st.columns(4)
            
            # First Half Macro Trackers
            if quarter == 1:
                g1.metric("1st Half Projection Anchor", "Waiting for Q2...", "Runs automatically in Q2")
                g2.metric("1st Half Score Actual", "0 pts", "Waiting for Q1 buzzer")
            else:
                g1.metric("1st Half Projection (Q1 x 2)", f"{q1_total * 2}.0 pts", "Macro Guide Anchor")
                g2.metric("1st Half Score Actual", f"{first_half_actual} pts", f"Q1: {q1_total} | Q2: {q2_total}")
                
            # Full Game Macro Trackers
            if quarter < 4:
                g3.metric("Full Game Projection (1H x 2)", "Waiting for Q4...", "Locks in at 4th Quarter")
                g4.metric("Current Running Game Total", f"{game_total} pts", f"Through Q{quarter}")
            else:
                g3.metric("Full Game Projection (1H x 2)", f"{first_half_actual * 2}.0 pts", "Macro Guide Anchor")
                g4.metric("Current Running Game Total", f"{game_total} pts", f"Live Q4 Tracking Active")

            # --- ROW 3: VARIANCE ARBITRAGE TABLE ---
            st.markdown("#### 📊 Multi-Platform Variance Matrix")
            
            poly_variance = mirror_pred - (base_quarter_line - 1.0)
            dk_variance = mirror_pred - base_quarter_line
            
            comparison_data = [
                {"Platform": "📡 ESPN Feed Data", "Market Mechanism": "Active Court Reality", "Line / Price Target": f"{q_total} Points", "Variance vs. Engine": "-- (Anchor)"},
                {"Platform": "📈 Polymarket Link", "Market Mechanism": "Peer-to-Peer Contracts", "Line / Price Target": f"O/U {base_quarter_line - 1.0} (54¢)", "Variance vs. Engine": f"{round(poly_variance, 1)} pts"},
                {"Platform": "🏛️ Kalshi Link", "Market Mechanism": "Regulated Financials", "Line / Price Target": f"O/U {base_quarter_line - 2.0} (60¢)", "Variance vs. Engine": f"{round(poly_variance - 1.0, 1)} pts"},
                {"Platform": "👑 DraftKings Link", "Market Mechanism": "Traditional House Line", "Line / Price Target": f"{base_quarter_line} Total O/U", "Variance vs. Engine": f"{round(dk_variance, 1)} pts"}
            ]
            
            st.table(comparison_data)
            
            # Live Midpoint Trigger Warnings
            if clock == mirror_time:
                if dk_variance <= -3.5:
                    st.error(f"🚨 **CRITICAL ADVANTAGE TRIGGERED:** Your projection ({mirror_pred}.0) is heavily UNDER the books. Target UNDER contracts!")
                elif dk_variance >= 3.5:
                    st.success(f"🚨 **CRITICAL ADVANTAGE TRIGGERED:** Your projection ({mirror_pred}.0) is heavily OVER the books. Target OVER contracts!")

time.sleep(refresh_rate)
st.rerun()
