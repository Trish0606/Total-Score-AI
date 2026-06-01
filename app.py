import streamlit as st
import pandas as pd
from src.ingestion import get_processed_game_data

st.set_page_config(page_title="Arbitrage AI Terminal", layout="wide")

# --- CSS TERMINAL STYLING ---
st.markdown("""
    <style>
    .stApp { background-color: #050505; }
    div[data-testid="stMetric"] { background-color: #0e1117; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
    h4 { color: #8b949e !important; text-transform: uppercase; letter-spacing: 1.5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🕹️ Control Room")
    league = st.selectbox("Select Target League", ["nba", "wnba"])
    
    params = {
        "nba": {"pace": 2.15, "baseline": 220.5, "mins": 48.0}, 
        "wnba": {"pace": 1.95, "baseline": 165.5, "mins": 40.0}
    }[league]
    
    st.divider()
    st.header("🤖 AI Analyst")
    if "messages" not in st.session_state: 
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): 
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ask about predictions..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): 
            st.markdown(prompt)

# --- CENTRALIZED DATA ---
all_games = get_processed_game_data(league)

# --- MAIN TERMINAL LAYOUT ---
tab1, tab2 = st.tabs(["🔴 LIVE TERMINAL", "📚 ARCHIVE & OUTLOOK"])

# ==================== TAB 1: LIVE OR UPCOMING ====================
with tab1:
    live_or_scheduled = [g for g in all_games if g.get("status") in ["IN_PROGRESS", "PRE"]]
    
    if not live_or_scheduled:
        st.info("No active or upcoming games right now.")
    else:
        for game in live_or_scheduled:
            status = game.get("status", "PRE").upper()
            st.title(f"🏀 {game['name']} Arbitrage Terminal")
            
            if status == "IN_PROGRESS":
                clock_val = game.get("clock", "10:00")
                parts = clock_val.split(":") if ":" in clock_val else ["0", "0"]
                elapsed_mins = params["mins"] - (float(parts[0]) + (float(parts[1]) / 60.0))
                
                pace_factor = game["total"] / elapsed_mins if elapsed_mins > 0.5 else 0
                pace_projection = pace_factor * params["mins"]
                ai_prediction = round(pace_projection, 1)

                st.markdown(f"#### 🎯 Game Flow Analytics (Status: {status})")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("1H Total", f"{game.get('1h_score', 0)} pts", delta="First Half")
                c2.metric("Total Score", game['total'], delta="Current Game")
                c3.metric("Pace Index", f"{pace_factor:.2f}", delta="Pts/Min Velocity")
                c4.metric("AI Pace Prediction", ai_prediction, delta="Projected Final")
                
                st.markdown("#### 🧠 Macro Game-Flow Guide")
                g1, g2, g3, g4 = st.columns(4)
                g1.metric("Baseline Projection", f"{params['baseline']} pts", delta="Market")
                g2.metric("Velocity Adjusted", f"{ai_prediction} pts", delta="Calculated")
                g3.metric("H2 Forecast", f"{round(pace_projection * 0.5, 1)}")
                g4.metric("Variance Delta", f"{round(pace_projection - params['baseline'], 1)}", delta="Edge")

                st.markdown("#### 📊 Multi-Platform Variance Matrix")
                base_book_line = params['baseline']
                platforms_data = [
                    {"Platform": "📈 Polymarket", "Total": base_book_line - 1.0},
                    {"Platform": "👑 DraftKings", "Total": base_book_line},
                    {"Platform": "🦁 BetMGM", "Total": base_book_line - 0.5},
                    {"Platform": "🔥 FanDuel", "Total": base_book_line + 0.5}
                ]
                
                matrix_rows = []
                for platform in platforms_data:
                    book_total = platform["Total"]
                    signal = "🟢 OVER" if ai_prediction > book_total else ("🔴 UNDER" if ai_prediction < book_total else "⚪ PUSH")
                    matrix_rows.append({"Platform": platform["Platform"], "Live Book Line": f"{book_total:.1f}", "Signal": signal})
                
                df = pd.DataFrame(matrix_rows)
                st.dataframe(df.style.map(lambda x: 'color: #00ff41; font-weight: bold;' if "OVER" in x else ('color: #ff3333; font-weight: bold;' if "UNDER" in x else ''), subset=['Signal']), use_container_width=True, hide_index=True)

            elif status == "PRE":
                st.warning(f"⏳ This matchup is scheduled but has not tipped off yet.")
                st.markdown("#### 🧠 Pre-Match Projections")
                c1, c2 = st.columns(2)
                c1.metric("Market Baseline Total", f"{params['baseline']} pts")
                c2.metric("Target Pace Environment", f"{params['pace']} pts/min")
                st.info("Live data parameters and platform signal grids automatically engage at tip-off.")

# ==================== TAB 2: ARCHIVE ====================
with tab2:
    st.subheader(f"🗓️ {league.upper()} Archive & Historical Outlook")
    
    # Strictly pull games marked as FINAL
    completed_games = [g for g in all_games if g.get("status") == "FINAL"]
    
    if not completed_games:
        st.info("No completed games found in the current API cycle.")
    else:
        archive_rows = []
        for past_game in completed_games:
            final_score = past_game.get("total", 0)
            closing_line = params["baseline"]
            net_delta = round(final_score - closing_line, 1)
            beaten_result = "📈 OVER" if final_score > closing_line else ("📉 UNDER" if final_score < closing_line else "⚪ PUSH")
            
            archive_rows.append({
                "Matchup": past_game.get("name", "Unknown Matchup"),
                "Final Score": f"{final_score} pts",
                "Market Closing Line": f"{closing_line} pts",
                "Closing Delta": f"{net_delta:+} pts",
                "Resulting Signal": beaten_result
            })
            
        archive_df = pd.DataFrame(archive_rows)
        
        def style_archive(val):
            if "OVER" in val: return 'color: #00ff41; font-weight: bold;'
            if "UNDER" in val: return 'color: #ff3333; font-weight: bold;'
            return ''
            
        st.dataframe(
            archive_df.style.map(style_archive, subset=['Resulting Signal']),
            use_container_width=True,
            hide_index=True
        )
