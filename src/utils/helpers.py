"""Helper functions"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.logger import setup_logger

logger = setup_logger(__name__)


def format_match_info(match: Dict, prediction: Optional[Dict] = None, odds: Optional[Dict] = None) -> str:
    """
    Format match information for display.
    Supports basic summary or enriched Markdown formatting with ML predictions and betting odds.
    """
    home_team = match.get("homeTeam", {}).get("name", "Unknown")
    away_team = match.get("awayTeam", {}).get("name", "Unknown")
    utc_date = match.get("utcDate", "")
    status = match.get("status", "SCHEDULED")
    
    try:
        match_date = datetime.fromisoformat(utc_date.replace('Z', '+00:00'))
        formatted_date = match_date.strftime("%H:%M")
    except:
        formatted_date = "TBD"
    
    # Si no se proporciona predicción, devolvemos el formato básico original
    if not prediction:
        return f"{home_team} vs {away_team} - {formatted_date} ({status})"
        
    # Si se incluye predicción, generamos el reporte estructurado en Markdown para Telegram
    try:
        probs = prediction.get("probabilities", {})
        home_prob = probs.get("HOME_WIN", 0.0) * 100
        draw_prob = probs.get("DRAW", 0.0) * 100
        away_prob = probs.get("AWAY_WIN", 0.0) * 100

        message = (
            f"📊 *Predicción:* {home_team} vs {away_team}\n"
            f"🕐 *Hora:* {formatted_date} ({status})\n\n"
            f"🤖 *Predicción del Modelo (XGBoost):*\n"
            f" └ 🟢 Victoria Local: `{home_prob:.1f}%`\n"
            f" └ 🟡 Empate: `{draw_prob:.1f}%`\n"
            f" └ 🔴 Victoria Visitante: `{away_prob:.1f}%`\n\n"
            f"💰 *Mejores Cuotas Encontradas:*\n"
        )

        if odds:
            if "home_win" in odds and odds["home_win"].get("odds") != "N/A":
                message += f" ├ Local: `{odds['home_win'].get('odds')}` ({odds['home_win'].get('bookmaker')})\n"
            else:
                message += f" ├ Local: `N/A`\n"
                
            if "draw" in odds and odds["draw"].get("odds") != "N/A":
                message += f" ├ Empate: `{odds['draw'].get('odds')}` ({odds['draw'].get('bookmaker')})\n"
            else:
                message += f" ├ Empate: `N/A`\n"
                
            if "away_win" in odds and odds["away_win"].get("odds") != "N/A":
                message += f" └ Visitante: `{odds['away_win'].get('odds')}` ({odds['away_win'].get('bookmaker')})\n"
            else:
                message += f" └ Visitante: `N/A`\n"
        else:
            message += " └ Cuotas no disponibles en este momento.\n"

        return message
    except Exception as e:
        logger.error(f"Error en format_match_info extendido: {e}")
        return f"{home_team} vs {away_team} - {formatted_date} ({status})"


def get_next_days_matches(days: int = 7) -> tuple:
    """Get date range for next N days"""
    today = datetime.now()
    next_date = today + timedelta(days=days)
    return today, next_date


def parse_match_result(result: str) -> Dict[str, int]:
    """Parse match result string (e.g., '3-1') into scores"""
    try:
        scores = result.split('-')
        return {"home": int(scores[0]), "away": int(scores[1])}
    except:
        return {"home": 0, "away": 0}


def get_match_outcome(home_score: int, away_score: int) -> str:
    """Get match outcome: HOME_WIN, AWAY_WIN, or DRAW"""
    if home_score > away_score:
        return "HOME_WIN"
    elif away_score > home_score:
        return "AWAY_WIN"
    else:
        return "DRAW"


def calculate_days_until_match(match_date_str: str) -> int:
    """Calculate days until match"""
    try:
        match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
        today = datetime.now(match_date.tzinfo)
        delta = (match_date - today).days
        return max(0, delta)
    except:
        return -1
