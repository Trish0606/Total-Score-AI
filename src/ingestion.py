import requests
import json
import streamlit as st

def get_processed_game_data(league):
    games = fetch_live_scores(league)
    processed = []
    
    for game in games:
        comp = game.get("competitions", [{}])[0]
        status = comp.get("status", {})
        
        # 1. FIX: Normalize ESPN lowercase states ('pre', 'in', 'post') 
        # to uppercase flags used by your app.py ('PRE', 'IN_PROGRESS', 'FINAL')
        raw_state = status.get("type", {}).get("state", "pre").lower()
        if raw_state == "in":
            app_status = "IN_PROGRESS"
        elif raw_state == "post":
            app_status = "FINAL"
        else:
            app_status = "PRE"
            
        # Calculate scores safely
        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            continue  # Skip malformed data payloads
            
        team1 = competitors[0].get("score", 0)
        team2 = competitors[1].get("score", 0)
        
        # Safe Quarter Index Extraction
        period = status.get("period", 1)
        idx = period - 1 if period > 0 else 0
        
        # Safe linescore fallback processing
        t1_lines = competitors[0].get("linescores", [])
        t2_lines = competitors[1].get("linescores", [])
        
        try:
            t1_q = int(t1_lines[idx].get("value", 0)) if idx < len(t1_lines) else 0
            t2_q = int(t2_lines[idx].get("value", 0)) if idx < len(t2_lines) else 0
            q_total = t1_q + t2_q
        except (IndexError, ValueError):
            q_total = 0
            
        processed.append({
            "name": game.get("name"),
            "status": app_status,  # Matches app.py filters perfectly now
            "clock": status.get("displayClock", "0:00"),
            "quarter": period,
            "total": int(team1) + int(team2),
            "q_total": q_total
        })
        
    return processed

def fetch_live_scores(league="wnba"):
    """
    Fetches real-time live game data directly from ESPN's hidden API endpoint.
    Leagues available: 'wnba' or 'nba'
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/{league}/scoreboard"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()
        return data.get("events", [])
    except Exception:
        return []

def fetch_schedule(league):
    return [
        {"game": "Aces vs. Sky", "tip_off": "8:00 PM"},
        {"game": "Liberty vs. Sun", "tip_off": "10:00 PM"}
    ]

@st.cache_data(ttl=20)
def fetch_book_line(platform):
    lines = {"Polymarket": 53.5, "Kalshi": 54.0, "DraftKings": 54.5}
    return lines.get(platform, 54.0)

def run_total_score_ai_rules(games):
    """
    Keeps your backend terminal debugger running alongside the streamlit client.
    """
    print("\n--- LIVE MATH PREDICTIONS ENGINE ---")
    for game in games:
        game_name = game.get("name")
        competition = game.get("competitions", [{}])[0]
        status = competition.get("status", {})
        type_state = status.get("type", {}).get("state", "").lower()
        
        if type_state != "in":
            continue
            
        clock_display = status.get("displayClock", "0:00")
        quarter = status.get("period", 1)
        
        try:
            minutes, seconds = map(int, clock_display.split(":"))
            time_remaining_in_quarter = minutes + (seconds / 60.0)
        except ValueError:
            continue
            
        competitors = competition.get("competitors", [])
        team1_total = int(competitors[0].get("score", 0))
        team2_total = int(competitors[1].get("score", 0))
        current_game_total = team1_total + team2_total
        
        t1_q_scores = [int(q.get("value", 0)) for q in competitors[0].get("linescores", [])]
        t2_q_scores = [int(q.get("value", 0)) for q in competitors[1].get("linescores", [])]
        
        if len(t1_q_scores) >= quarter and len(t2_q_scores) >= quarter:
            current_quarter_total = t1_q_scores[quarter-1] + t2_q_scores[quarter-1]
        else:
            current_quarter_total = 0

        print(f"\n🏀 Game: {game_name} | Q{quarter} Clock: {clock_display}")
        print(f"   Current Game Total: {current_game_total} | Current Q{quarter} Total: {current_quarter_total}")

        if clock_display == "6:00":
            mirror_prediction = current_quarter_total * 2
            print(f"   🚨 TRIGGER [6-Min Mirror]: Q{quarter} projected total score is: {mirror_prediction}")

        points_left_prediction = current_quarter_total + (time_remaining_in_quarter * 5)
        print(f"   📊 VELOCITY [5 pts/min rule]: Projected Q{quarter} score ends at: {round(points_left_prediction, 1)}")

if __name__ == "__main__":
    wnba_live = fetch_live_scores("wnba")
    run_total_score_ai_rules(wnba_live)
