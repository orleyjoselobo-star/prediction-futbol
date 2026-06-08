"""Helper functions"""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.logger import setup_logger

logger = setup_logger(__name__)


def format_match_info(match: Dict) -> str:
    """Format match information for display"""
    home_team = match.get("homeTeam", {}).get("name", "Unknown")
    away_team = match.get("awayTeam", {}).get("name", "Unknown")
    utc_date = match.get("utcDate", "")
    status = match.get("status", "SCHEDULED")
    
    try:
        match_date = datetime.fromisoformat(utc_date.replace('Z', '+00:00'))
        formatted_date = match_date.strftime("%H:%M")
    except:
        formatted_date = "TBD"
    
    return f"{home_team} vs {away_team} - {formatted_date} ({status})"


def get_next_days_matches(days: int = 7) -> datetime:
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
