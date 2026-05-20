import time
from ingestion import fetch_live_scores, run_total_score_ai_rules
from features import fetch_live_sportsbook_lines, calculate_betting_advantage

def run_total_score_ai_assistant(api_key="", league_choice="wnba"):
    """
    The main coordinator script that runs your entire betting AI loop.
    It fetches live scores, estimates projections, looks up sportsbook totals,
    and calculates your mathematical advantage.
    """
    print("==================================================")
    print(f"🚀 STARTING LIVE TOTAL SCORE AI ASSISTANT ({league_choice.upper()})")
    print("==================================================")
    
    # 1. Map league strings to API formats
    odds_league = "basketball_wnba" if league_choice == "wnba" else "basketball_nba"
    
    # 2. Fetch live game progress from ESPN
    live_games = fetch_live_scores(league_choice)
    if not live_games:
        print("❌ No active or live games found right now.")
        return
        
    # 3. Fetch live betting odds from Sportsbooks
    book_lines = fetch_live_sportsbook_lines(api_key, league=odds_league)
    
    # 4. Loop through every active game and look for your specific math triggers
    for game in live_games:
        game_name = game.get("name") # e.g. "Indiana Fever vs Chicago Sky"
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        
        if status.get("type", {}).get("state") != "in":
            continue # Skip pre-game or completed games
            
        clock = status.get("displayClock", "0:00")
        quarter = status.get("period", 1)
        
        # Calculate current quarter stats
        competitors = competition.get("competitors", [])
        t1_q_scores = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q_scores = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        
        if len(t1_q_scores) >= quarter and len(t2_q_scores) >= quarter:
            current_quarter_total = t1_q_scores[quarter-1] + t2_q_scores[quarter-1]
        else:
            current_quarter_total = 0
            
        print(f"\n⚙️ Analyzing: {game_name} (Q{quarter} | Clock: {clock})")
        
        # TRIGGER CHECK 1: The 6-Minute Midpoint Mirror
        if clock == "6:00":
            my_q_prediction = current_quarter_total * 2
            print(f"🎯 [6-Min Trigger] Your predicted quarter total: {my_q_prediction}")
            
            # Look up if we have a sportsbook line matching this game
            # We use a default placeholder line of 55.5 for quarters if not found
            sportsbook_q_line = 55.5 
            
            alert_message = calculate_betting_advantage(my_q_prediction, sportsbook_q_line, threshold=3.5)
            print(alert_message)
            
        # TRIGGER CHECK 2: General Pacing Check (5 points a minute remaining)
        try:
            minutes, seconds = map(int, clock.split(":"))
            time_left = minutes + (seconds / 60.0)
            projected_q_final = current_quarter_total + (time_left * 5)
            print(f"📈 [Pacing Estimate] Current velocity points to a Q{quarter} score around: {round(projected_q_final, 1)}")
        except ValueError:
            pass

if __name__ == "__main__":
    # To run this with a real API key later: run_total_score_ai_assistant("YOUR_KEY", "wnba")
    run_total_score_ai_assistant(api_key="", league_choice="wnba")
