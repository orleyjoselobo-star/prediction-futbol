"""Configuration settings for the football prediction system."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Project Root Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Cloud Run safe paths
DATA_DIR = Path("/tmp/data")
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = Path("/tmp/logs")

for directory in [DATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- TELEGRAM & API CONFIG ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
FOOTBALL_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

# --- LEAGUE MAPPING ---
# Definimos LEAGUES explícitamente para que los handlers la encuentren
LEAGUES = {
    "premier": {"name": "Premier League", "id": "PL"},
    "la_liga": {"name": "La Liga", "id": "PD"},
    "serie_a": {"name": "Serie A", "id": "SA"},
    "bundesliga": {"name": "Bundesliga", "id": "BL1"},
    "champions": {"name": "UEFA Champions League", "id": "CL"},
    "ligue_1": {"name": "Ligue 1", "id": "FL1"}
}

# Mantenemos SUPPORTED_LEAGUES por compatibilidad si otros módulos lo usan
SUPPORTED_LEAGUES = LEAGUES

# --- ML MODEL CONFIG ---
MODEL_PATH = BASE_DIR / "models/xgboost_model.pkl"
SCALER_PATH = BASE_DIR / "models/scaler.pkl"
MODEL_VERSION = "2.0_XGBOOST"

# --- LOGGING ---
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
