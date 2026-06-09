"""Module for loading trained Machine Learning models and executing match predictions."""

import joblib
import os
import pandas as pd
from typing import Dict, Any
from src.config.settings import MODEL_PATH, SCALER_PATH
from src.logger import setup_logger

logger = setup_logger(__name__)

class MatchPredictor:
    """Handles ML model loading and real-time match outcome inference."""

    def __init__(self):
        self.model_path = MODEL_PATH
        self.scaler_path = SCALER_PATH
        self.model = None
        self.scaler = None
        self._load_models()

    def _load_models(self):
        """Loads the pre-trained XGBoost/LightGBM model and scaler artifacts safely."""
        try:
            # Verificar y cargar el modelo predictivo
            if os.path.exists(self.model_path):
                logger.info(f"Cargando modelo de Machine Learning desde: {self.model_path}")
                self.model = joblib.load(self.model_path)
            else:
                logger.warning(f"No se encontró el archivo del modelo en {self.model_path}. Se usará modo de inferencia analítica auxiliar.")

            # Verificar y cargar el escalador de variables si aplica
            if os.path.exists(self.scaler_path):
                logger.info(f"Cargando escalador de características desde: {self.scaler_path}")
                self.scaler = joblib.load(self.scaler_path)
        except Exception as e:
            logger.error(f"Error crítico al cargar los artefactos de Machine Learning: {e}")

    def predict(self, feature_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Executes match outcome inference over the input feature matrix.
        Retorna las probabilidades calculadas por el modelo XGBoost o una distribución matemática de respaldo.
        """
        # Valores por defecto totalmente seguros y equitativos (33.3% para cada escenario)
        prediction_result = {
            "prediction": "DRAW",
            "probabilities": {
                "HOME_WIN": 0.333,
                "DRAW": 0.334,
                "AWAY_WIN": 0.333
            }
        }

        try:
            # Si el DataFrame es nulo o viene completamente vacío, devolvemos base balanceada directamente
            if feature_df is None or feature_df.empty:
                logger.warning("Se recibió una matriz de características vacía para la predicción. Retornando baseline balanceado.")
                return prediction_result

            # Aplicar escalado a los datos si el escalador está disponible
            X_scaled = feature_df.copy()
            if self.scaler:
                logger.debug("Aplicando transformación de escala a las variables de entrada.")
                X_scaled = self.scaler.transform(feature_df)

            # --- CASO A: Ejecutar la inferencia real si el modelo XGBoost está cargado ---
            if self.model:
                logger.info("Ejecutando inferencia en tiempo real con el modelo XGBoost.")
                
                # Obtener las probabilidades de cada clase (0: HOME_WIN, 1: DRAW, 2: AWAY_WIN)
                prob_array = self.model.predict_proba(X_scaled)[0]
                
                # Mapear el array resultante al diccionario de salida esperado por el bot
                prediction_result["probabilities"]["HOME_WIN"] = float(prob_array[0])
                prediction_result["probabilities"]["DRAW"] = float(prob_array[1])
                prediction_result["probabilities"]["AWAY_WIN"] = float(prob_array[2])
                
                # Determinar el resultado con mayor probabilidad estadística
                classes = ["HOME_WIN", "DRAW", "AWAY_WIN"]
                prediction_result["prediction"] = classes[prob_array.argmax()]
                
            # --- CASO B: Lógica analítica de respaldo segura si el archivo .pkl no está ---
            else:
                logger.info("Usando motor analítico de respaldo seguro (Baseline paramétrico).")
                
                # Extracción segura controlando celdas vacías o faltantes para evitar IndexErrors
                form_diff = 0.0
                if "form_recent" in feature_df.columns and len(feature_df) > 0:
                    form_diff = float(feature_df["form_recent"].iloc[0])

                goals_diff = 0.0
                if "goals_for" in feature_df.columns and len(feature_df) > 0:
                    goals_diff = float(feature_df["goals_for"].iloc[0])
                
                # Simulación matemática basada en las diferencias de fuerza para no romper el flujo del bot
                base_home = 0.40 + (form_diff * 0.2) + (goals_diff * 0.05)
                base_away = 0.32 - (form_diff * 0.2) - (goals_diff * 0.05)
                
                # Asegurar límites lógicos estables entre 0.1 y 0.8
                base_home = max(0.1, min(0.8, base_home))
                base_away = max(0.1, min(0.8, base_away))
                base_draw = 1.0 - base_home - base_away
                
                prediction_result["probabilities"]["HOME_WIN"] = round(base_home, 3)
                prediction_result["probabilities"]["DRAW"] = round(base_draw, 3)
                prediction_result["probabilities"]["AWAY_WIN"] = round(base_away, 3)
                
                valores = [base_home, base_draw, base_away]
                classes = ["HOME_WIN", "DRAW", "AWAY_WIN"]
                prediction_result["prediction"] = classes[valores.index(max(valores))]

            logger.info(f"Predicción completada con éxito. Resultado más probable: {prediction_result['prediction']}")

        except Exception as e:
            logger.error(f"Error durante la ejecución de la inferencia del modelo: {e}", exc_info=True)
            # En caso de cualquier falla imprevista, nos aseguramos de que devuelva el objeto base estructurado
            return prediction_result

        return prediction_result
