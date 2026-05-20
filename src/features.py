import requests

def fetch_live_sportsbook_lines(api_key, league="basketball_nba"):
    """
    Fetches real-time live Over/Under betting lines from sportsbooks.
    Leagues: 'basketball_nba' or 'basketball_wnba'
    """
    # If no real API key is provided yet, we return mock data so the script doesn't crash
    if api_key == "YOUR_API_KEY_HERE" or not api_key:
        print("⚠️ Using placeholder sportsbook lines (Get a free API key at theoddsapi.com)")
        return {
            "New York Liberty vs Las Vegas Aces": 165.5,
            "Los Angeles Sparks vs Seattle Storm": 158.5,
            "Indiana Fever vs Chicago Sky": 162.0
        }

    url = f"https://api.the-odds-api.com/v4/sports/{league}/odds/"
    params = {
        "apiKey": api_key,
        "regions": "us",
        "markets": "totals", # Fetches Over/Under lines
        "oddsFormat": "decimal"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Failed to pull live lines from Odds API")
        return {}
        
    odds_data = response.json()
    live_lines = {}
    
    # Extract the total line for each game
    for game in odds_data:
        home_team = game.get("home_team")
        away_team = game.get("away_team")
        game_key = f"{away_team} @ {home_team}"
        
        # Look inside bookmakers (e.g., DraftKings, FanDuel)
        bookmakers = game.get("bookmakers", [])
        if bookmakers:
            # Grab the first available sportsbook's line
            markets = bookmakers[0].get("markets", [])
            if markets:
                outcomes = markets[0].get("outcomes", [])
                for outcome in outcomes:
                    if outcome.get("name") == "Over":
                        live_lines[game_key] = outcome.get("point")
                        break
                        
    return live_lines

def calculate_betting_advantage(my_prediction, sportsbook_line, threshold=4.0):
    """
    Compares your 80% math prediction against the live sportsbook line.
    Flags a BET signal if the gap is larger than your comfort threshold.
    """
    gap = my_prediction - sportsbook_line
    
    print(f"     [AI Evaluation] Your Math: {my_prediction} vs Book Line: {sportsbook_line} | Gap: {round(gap, 1)}")
    
    if gap >= threshold:
        return f"🚨🚨 OVER ALERT: Your math indicates high scoring value. Advantage: +{round(gap, 1)} points!"
    elif gap <= -threshold:
        return f"🚨🚨 UNDER ALERT: Your math indicates heavy scoring slowdown. Advantage: {round(gap, 1)} points!"
    else:
        return "⏳ No significant line variance detected. Hold bet."
