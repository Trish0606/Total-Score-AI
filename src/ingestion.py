import requests
import json
import streamlit as st

def get_processed_game_data(league):
    games = fetch_live_scores(league)
    processed = []
    
    for game in games:
        comp = game.get("competitions", [{}])[0]
        status = comp.get("status", {})
        
        # Normalize ESPN states ('pre', 'in', 'post') to uppercase flags
        raw_state = status.get("type", {}).get("state", "pre").lower()
        if raw_state == "in":
            app_status = "IN_PROGRESS"
        elif raw_state == "post":
            app_status = "FINAL"
        else:
            app_status = "PRE"
            
        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            continue
            
        team1 = competitors[0].get("score", 0)
        team2 = competitors[1].get("score", 0)
        
        period = status.get("period", 1)
        idx = period - 1 if period > 0 else 0
        
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
            "status": app_status,
            "clock": status.get("displayClock", "0:00"),
            "quarter": period,
            "total": int(team1) + int(team2),
            "q_total": q_total
        })
        
    return processed

def fetch_live_scores(league="wnba"):
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/{league}/scoreboard"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return []
        data = response.json()
        return data.get("events", [])
    except Exception:
        return []

@st.cache_data(ttl=20)
def fetch_book_line(platform):
    lines = {"Polymarket": 53.5, "Kalshi": 54.0, "DraftKings": 54.5}
    return lines.get(platform, 54.0)
