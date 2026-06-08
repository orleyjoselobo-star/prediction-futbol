"""Module for processing raw football data and preparing feature matrices for ML models."""

import numpy as np
import pandas as pd
from typing import Dict, Any
from src.logger import setup_logger

logger = setup_logger(__name__)

class DataProcessor:
    """Handles data transformation, feature calculation, and alignment for prediction."""

    def __init__(self):
        # Mapeo exacto de las columnas que tu modelo entrenado de XGBoost/LightGBM espera recibir
        self.feature_columns = [
            "form_recent",
            "head_to_head",
            "table_position",
            "goals_for",
            "goals_against",
            "current_streak",
            "home_advantage"
        ]

    def calculate_team_features(self, historical_data: pd.DataFrame, team_name: str) -> Dict[str, float]:
        """
        Calculates granular performance features for a specific team using historical match data.
        Si no hay suficientes datos históricos en el DataFrame, genera promedios base consistentes.
        """
        logger.info(f"Calculando variables de rendimiento para el equipo: '{team_name}'")
        
        # Estructura de diccionario base con métricas por defecto
        features = {
            "form_recent": 0.50,       # Estado de forma neutral (escala 0 a 1)
            "table_position": 10.0,    # Posición media supuesta en la tabla
            "goals_for": 1.20,         # Promedio de goles anotados base
            "goals_against": 1.20,     # Promedio de goles recibidos base
            "current_streak": 0.0,      # Racha neutral de partidos (Victorias - Derrotas)
            "home_advantage": 0.15     # Factor base de ventaja de jugar en casa
        }

        try:
            if historical_data.empty:
                logger.debug(f"DataFrame histórico vacío para {team_name}. Usando métricas base predeterminadas.")
                return features

            # Filtrar partidos donde el equipo participó (ya sea de local o visitante)
            team_matches = historical_data[
                (historical_data["home_team"] == team_name) | 
                (historical_data["away_team"] == team_name)
            ].sort_values(by="date", ascending=False)

            if len(team_matches) > 0:
                # Tomar los últimos 5 partidos para medir el estado de forma reciente
                recent_matches = team_matches.head(5)
                puntos_obtenidos = []
                goles_anotados = []
                goles_recibidos = []

                for _, match in recent_matches.iterrows():
                    is_home = match["home_team"] == team_name
                    goals_f = match["home_goals"] if is_home else match["away_goals"]
                    goals_a = match["away_goals"] if is_home else match["home_goals"]
                    
                    goles_anotados.append(goals_f)
                    get_goles_recibidos = goles_recibidos.append(goals_a)

                    # Calcular puntos por partido (Victoria=3, Empate=1, Derrota=0)
                    if goals_f > goals_a:
                        puntos_obtenidos.append(3)
                    elif goals_f == goals_a:
                        puntos_obtenidos.append(1)
                    else:
                        puntos_obtenidos.append(0)

                # Actualizar los features reales calculados con Pandas/NumPy
                features["form_recent"] = float(np.mean(puntos_obtenidos) / 3.0)
                features["goals_for"] = float(np.mean(goles_anotados))
                features["goals_against"] = float(np.mean(goles_recibidos))
                features["current_streak"] = float(np.sum([1 if p == 3 else -1 if p == 0 else 0 for p in puntos_obtenidos]))

        except Exception as e:
            logger.error(f"Error procesando métricas avanzadas de Pandas para {team_name}: {e}")

        return features

    def prepare_features_for_prediction(self, home_features: Dict[str, float], away_features: Dict[str, float]) -> pd.DataFrame:
        """
        Combines home and away team profiles into a singular standardized feature matrix (DataFrame)
        aligned precisely with the input schema requirements of the Machine Learning predictor.
        """
        logger.info("Consolidando matriz diferencial de variables (Home vs Away) para inferencia de Machine Learning.")
        
        # En modelos de clasificación predictiva 1X2, se suele calcular la diferencia neta de fuerzas
        combined_data = {
            "form_recent": home_features.get("form_recent", 0.5) - away_features.get("form_recent", 0.5),
            "head_to_head": 0.0, # Se computará cruzando registros directos históricos
            "table_position": away_features.get("table_position", 10.0) - home_features.get("table_position", 10.0), # Invertido porque menor posición es mejor
            "goals_for": home_features.get("goals_for", 1.2) - away_features.get("goals_for", 1.2),
            "goals_against": away_features.get("goals_against", 1.2) - home_features.get("goals_against", 1.2), # Menos goles en contra es mejor
            "current_streak": home_features.get("current_streak", 0.0) - away_features.get("current_streak", 0.0),
            "home_advantage": home_features.get("home_advantage", 0.15)
        }

        # Generar el DataFrame con una sola fila para la predicción en tiempo real
        df_features = pd.DataFrame([combined_data])
        
        # Asegurar el orden exacto de las columnas que el modelo XGBoost guardó originalmente al entrenarse
        df_features = df_features.reindex(columns=self.feature_columns, fill_value=0.0)
        
        return df_features
