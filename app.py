@st.fragment(run_every=10)
    def render_live_terminal():
        active_games = get_processed_game_data(league)
        if not active_games:
            st.info("No active games right now. Check back at tip-off.")
            return

        for game in active_games:
            # 1. Determine State
            game_status = game.get("status", "SCHEDULED") # e.g., 'IN_PROGRESS', 'HALFTIME', 'FINAL'
            
            st.title(f"🏀 {game['name']} Arbitrage Terminal")
            
            # 2. Dynamic Metric Calculation
            if game_status == "IN_PROGRESS":
                clock_val = game.get("clock", "12:00")
                parts = clock_val.split(":") 
                # Assuming WNBA games are 40 mins (4 quarters of 10 mins)
                total_game_mins = 40.0 
                elapsed_mins = total_game_mins - (float(parts[0]) + (float(parts[1]) / 60.0))
                pace_factor = game["total"] / elapsed_mins if elapsed_mins > 0.5 else 0
                pace_projection = pace_factor * total_game_mins
            else:
                pace_projection = 0.0
                pace_factor = 0.0

            # 3. Dynamic UI Rendering
            st.markdown(f"#### 🎯 Game Flow Analytics (Status: {game_status})")
            c1, c2, c3, c4 = st.columns(4)
            
            # Using dynamic game data instead of "52 pts"
            c1.metric("Current Period", game.get("period", "N/A"))
            c2.metric("Total Score", game.get('total', 0))
            c3.metric("Pace Index", f"{pace_factor:.2f}")
            c4.metric("AI Pace Prediction", round(pace_projection, 1))
            
            # ... [Keep your existing Macro Game-Flow Guide here] ...
