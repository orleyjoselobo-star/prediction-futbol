"""Configuration settings for the football prediction system."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# APIs
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./prediction_futbol.db")
FIRESTORE_CREDENTIALS = os.getenv("FIRESTORE_CREDENTIALS_PATH")

# Betting APIs
BETING_API_KEYS = {
    "betesporte": os.getenv("BETESPORTE_API_KEY"),
    "pinnacle": os.getenv("PINNACLE_API_KEY"),
}

# Model settings
MODEL_PATH = MODELS_DIR / "prediction_model.pkl"
MODEL_VERSION = "1.0"
MIN_PREDICTION_CONFIDENCE = 0.60

# League configurations
SUPPORTED_LEAGUES = {
    "PL": "Premier League",
    "LA": "La Liga",
    "SA": "Serie A",
    "BL": "Bundesliga",
    "FL1": "Ligue 1",
    "CAT_A": "Categoría A Colombia",
    "CAT_B": "Categoría B Colombia",
    "CL": "UEFA Champions League",
    "WC": "World Cup 2026",
}

# Features for prediction
TARGET_FEATURES = [
    "form_recent",
    "head_to_head",
    "table_position",
    "goals_for",
    "goals_against",
    "current_streak",
    "home_advantage",
    "injuries",
]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
