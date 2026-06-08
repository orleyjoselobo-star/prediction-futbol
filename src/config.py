"""Configuration management for the application"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Telegram Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")

# Firebase Configuration
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

# APIs Configuration
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

# Betting APIs
BET365_API_KEY = os.getenv("BET365_API_KEY")
BWIN_API_KEY = os.getenv("BWIN_API_KEY")
BETANO_API_KEY = os.getenv("BETANO_API_KEY")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Model Configuration
MODEL_PATH = MODELS_DIR / "xgboost_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Leagues Configuration
LEAGUES = {
    "premier_league": {"id": "PL", "country": "England", "name": "Premier League"},
    "la_liga": {"id": "LA", "country": "Spain", "name": "La Liga"},
    "serie_a": {"id": "SA", "country": "Italy", "name": "Serie A"},
    "bundesliga": {"id": "BL1", "country": "Germany", "name": "Bundesliga"},
    "ligue_1": {"id": "FL1", "country": "France", "name": "Ligue 1"},
    "colombian_league": {"id": "CL", "country": "Colombia", "name": "Categoria A"},
    "mls": {"id": "MLS", "country": "United States", "name": "MLS"},
    "world_cup_2026": {"id": "WC", "country": "International", "name": "World Cup 2026"},
}

# Model Configuration
MODEL_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "n_estimators": 100,
    "max_depth": 7,
    "learning_rate": 0.1,
}
