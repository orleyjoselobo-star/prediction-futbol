"""Module for fetching live and historical football data from external APIs."""

import requests
from typing import Dict, Any, Optional
from src.config.settings import FOOTBALL_API_KEY
from src.logger import setup_logger

logger = setup_logger(__name__)

class FootballDataFetcher:
    """Handles authentication and HTTP requests to retrieve match and league data."""

    def __init__(self):
        # Base URL para football-data.org (basado en el mapa de variables y requerimientos)
        self.base_url = "https://api.football-data.org/v4"
        self.api_key = FOOTBALL_API_KEY
        self.headers = {
            "X-Auth-Token": self.api_key if self.api_key else ""
        }

    def _execute_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a safe GET request to the external API resource."""
        if not self.api_key or self.api_key == "your_football_data_api_key":
            logger.error("FOOTBALL_DATA_API_KEY no configurado o mantiene el valor por defecto.")
            return {"count": 0, "matches": []}

        url = f"{self.base_url}/{endpoint}"
        try:
            logger.info(f"Consumiendo endpoint: {endpoint} | Parámetros: {params}")
            response = requests.get(url, headers=self.headers, params=params, timeout=12)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión con la API de fútbol en el endpoint [{endpoint}]: {e}")
            return {"count": 0, "matches": []}

    def get_league_matches(self, league_code: str) -> Dict[str, Any]:
        """
        Fetches scheduled matches for a specific league code.
        Filtra por defecto los partidos programados del día actual.
        """
        if not league_code:
            logger.warning("Se solicitó get_league_matches pero el league_code está vacío.")
            return {"matches": []}

        # Estructura del endpoint de football-data para partidos de una competición
        endpoint = f"competitions/{league_code}/matches"
        
        # Opcional: Filtrar por la fecha actual o el estado 'SCHEDULED' si la API lo soporta directamente
        # En entornos de desarrollo, si no hay partidos hoy, se puede omitir el filtro de fecha para pruebas.
        params = {
            "status": "SCHEDULED"
        }
        
        logger.info(f"Buscando partidos agendados para la liga/competición: {league_code}")
        result = self._execute_get(endpoint, params=params)
        
        # Retornar con la estructura esperada por el handler de Telegram
        return {
            "count": result.get("count", 0),
            "matches": result.get("matches", [])
        }

    def get_match_history(self, match_id: str) -> Dict[str, Any]:
        """Retrieves head-to-head records or historical statistics for a specific match context."""
        endpoint = f"matches/{match_id}"
        return self._execute_get(endpoint)
