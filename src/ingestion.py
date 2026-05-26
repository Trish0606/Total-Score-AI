import requests
import json
import streamlit as st
# In src/ingestion.py
def fetch_live_scores(league):
    # ... your existing code ...
    return live_games

def fetch_schedule(league):
    # This is a placeholder until you write the actual logic
    return [
        {"game": "Aces vs. Sky", "tip_off": "8:00 PM"},
        {"game": "Liberty vs. Sun", "tip_off": "10:00 PM"}
    ]
@st.cache_data(ttl=20) # Cache for 20 seconds to avoid blocking
def fetch_book_line(platform):
    # REPLACE THESE WITH YOUR ACTUAL SCRAPING LOGIC
    # Example: return requests.get("https://api.polymarket.com/...").json()['price']
    
    # Mock data for now:
    lines = {"Polymarket": 53.5, "Kalshi": 54.0, "DraftKings": 54.5}
    return lines.get(platform, 54.0)
def fetch_live_scores(league="wnba"):
    """
    Fetches real-time live game data directly from ESPN's hidden API endpoint.
    Leagues available: 'wnba' or 'nba'
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/{league}/scoreboard"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Failed to pull data from ESPN")
        return []
        
    data = response.json()
    return data.get("events", [])

def run_total_score_ai_rules(games):
    """
    Applies your exact 80% math rules:
    1. 6-minute mark: 2x the current quarter score.
    2. Any point in quarter: Remaining minutes * 5 points.
    3. End of Q3: Flags a projection based on the current score + 60.
    """
    print("\n--- LIVE MATH PREDICTIONS ENGINE ---")
    
    for game in games:
        game_name = game.get("name")
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        type_state = status.get("type", {}).get("state") # 'pre', 'in', or 'post'
        
        # We only care about active, live games
        if type_state != "in":
            continue
            
        # Get live clock and quarter info
        clock_display = status.get("displayClock", "0:00") # e.g. "6:00" or "3:15"
        quarter = status.get("period", 1)
        
        # Calculate numeric minutes remaining in current quarter
        try:
            minutes, seconds = map(int, clock_display.split(":"))
            time_remaining_in_quarter = minutes + (seconds / 60.0)
        except ValueError:
            continue
            
        # Extract live team scores
        competitors = competition.get("competitors", [])
        team1_total = int(competitors[0].get("score", 0))
        team2_total = int(competitors[1].get("score", 0))
        current_game_total = team1_total + team2_total
        
        # For quarter specific tracking, grab the specific linescores (points per quarter)
        t1_q_scores = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q_scores = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        
        # Calculate current score for just this active quarter
        if len(t1_q_scores) >= quarter and len(t2_q_scores) >= quarter:
            current_quarter_total = t1_q_scores[quarter-1] + t2_q_scores[quarter-1]
        else:
            current_quarter_total = 0

        print(f"\n🏀 Game: {game_name} | Q{quarter} Clock: {clock_display}")
        print(f"   Current Game Total: {current_game_total} | Current Q{quarter} Total: {current_quarter_total}")

        # RULE 1: The 6-Minute Midpoint Mirror (2x Score)
        if clock_display == "6:00":
            mirror_prediction = current_quarter_total * 2
            print(f"   🚨 TRIGGER [6-Min Mirror]: Q{quarter} projected total score is: {mirror_prediction}")
            print(f"   👉 ACTION: Compare against live quarter sportsbook line. If book is far from {mirror_prediction}, bet variance!")

        # RULE 2: General 5 Points a Minute Projection
        points_left_prediction = current_quarter_total + (time_remaining_in_quarter * 5)
        print(f"   📊 VELOCITY [5 pts/min rule]: Projected Q{quarter} score ends at: {round(points_left_prediction, 1)}")

        # RULE 3: End of 3rd Quarter (The 60-Point Book Deficit Exploit)
        if quarter == 3 and clock_display == "0:00":
            lazy_sportsbook_line = current_game_total + 60.5
            print(f"   🚨 TRIGGER [End of Q3]: Sportsbook estimated line will default to around: {lazy_sportsbook_line}")
            print(f"   👉 METHOD CHECK: If teams are pacing faster than 20pts/quarter, bet the OVER.")

if __name__ == "__main__":
    # Test it with live WNBA data
    wnba_live = fetch_live_scores("wnba")
    run_total_score_ai_rules(wnba_live)
