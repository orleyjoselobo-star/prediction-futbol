"""Data fetching layer for football-data.org API."""

import requests
from src.config.settings import FOOTBALL_API_KEY
from src.logger import setup_logger

logger = setup_logger(__name__)

class FootballDataFetcher:
    def __init__(self):
        self.api_key = FOOTBALL_API_KEY
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": self.api_key}

    def get_league_matches(self, league_id: str) -> dict:
        """Obtiene los próximos partidos agendados de la liga."""
        try:
            url = f"{self.base_url}/competitions/{league_id}/matches?status=SCHEDULED"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo partidos: {e}")
            return {"matches": []}

    def get_league_standings(self, league_id: str) -> dict:
        """Obtiene la tabla de posiciones y rachas de la liga."""
        try:
            url = f"{self.base_url}/competitions/{league_id}/standings"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo tabla de posiciones: {e}")
            return {}
