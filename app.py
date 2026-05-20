import streamlit as st
from src.ingestion import fetch_live_scores, fetch_book_line # Import the new function

# ... (Previous code remains the same)

# 3. Inside your 'for game in live_games:' loop:
        
        # Pull live lines from books instead of using static base_quarter_line
        market_lines = {
            "📈 Polymarket": fetch_book_line("Polymarket"),
            "🏛️ Kalshi": fetch_book_line("Kalshi"),
            "👑 DraftKings": fetch_book_line("DraftKings")
        }

        # Calculate Variance against the live Market Line
        # We now use the mirror_pred (your engine) vs the live book line
        comparison_data = []
        for platform, market_total in market_lines.items():
            variance = mirror_pred - market_total
            
            # Logic: Signal driven by Variance against the live Market Line
            def get_signal(var):
                if var > 1.5: return "📈 OVER"
                if var < -1.5: return "📉 UNDER"
                return "➖ NEUTRAL"

            comparison_data.append({
                "Platform": platform,
                "Live Market Total": market_total, # This is the book's score
                "Engine Projection": f"{mirror_pred:.1f}",
                "Variance": f"{variance:.1f}",
                "Signal": get_signal(variance)
            })
            
        st.table(comparison_data)
