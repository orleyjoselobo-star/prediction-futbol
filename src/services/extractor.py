"""Service layer to extract data from API-Football."""
import requests
from typing import Dict, Any, List, Optional
from src.config.settings import API_FOOTBALL_KEY, FOOTBALL_API_KEY
from src.logger import setup_logger

logger = setup_logger(__name__)

class FootballAPIExtractor:
    """Handles direct HTTP requests to the API-Football service."""
    
    def __init__(self):
        self.base_url = "https://v3.football.api-sports.io"
        # Usar la primera clave disponible de la configuración
        self.api_key = API_FOOTBALL_KEY or FOOTBALL_API_KEY
        self.headers = {
            "x-rapidapi-host": "v3.football.api-sports.io",
            "x-rapidapi-key": self.api_key if self.api_key else ""
        }

    def _execute_get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a GET request to the specified API endpoint safely."""
        if not self.api_key:
            logger.error("API Key para API-Football no configurada.")
            return {"results": 0, "response": []}

        url = f"{self.base_url}/{endpoint}"
        try:
            logger.info(f"Realizando petición GET a: {endpoint} con parámetros: {params}")
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            # Verificar si la API retornó errores internos en su payload
            if data.get("errors"):
                logger.warning(f"La API retornó alertas de error: {data['errors']}")
                
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de red al conectar con API-Football ({endpoint}): {e}")
            return {"results": 0, "response": []}

    def obtener_partidos_del_dia(self, league_id: int, date_str: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los partidos programados para una fecha específica y una liga.
        date_str debe venir en formato 'YYYY-MM-DD'
        """
        params = {
            "league": league_id,
            "date": date_str,
            "season": datetime.now().year if hasattr(datetime, 'now') else 2026
        }
        # Corrección dinámica del año actual para el parámetro season si es necesario
        from datetime import datetime
        params["season"] = datetime.now().year

        result = self._execute_get("fixtures", params=params)
        return result.get("response", [])

    def obtener_estadisticas_equipo(self, league_id: int, team_id: int, season: int) -> Dict[str, Any]:
        """Obtiene el rendimiento, goles y rachas de un equipo en una temporada dada."""
        params = {
            "league": league_id,
            "team": team_id,
            "season": season
        }
        result = self._execute_get("teams/statistics", params=params)
        return result.get("response", {})

    def obtener_historial_h2h(self, team_a_id: int, team_b_id: int) -> List[Dict[str, Any]]:
        """Obtiene los últimos enfrentamientos directos (Head to Head) entre dos equipos."""
        params = {
            "h2h": f"{team_a_id}-{team_b_id}"
        }
        result = self._execute_get("fixtures/headtohead", params=params)
        return result.get("response", [])

    def obtener_tabla_posiciones(self, league_id: int, season: int) -> List[Dict[str, Any]]:
        """Obtiene la tabla de clasificación actual de una liga."""
        params = {
            "league": league_id,
            "season": season
        }
        result = self._execute_get("standings", params=params)
        return result.get("response", [])
