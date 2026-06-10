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

# --- ENVIRONMENT & SYSTEM CONFIGURATION ---
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- FOOTBALL DATA APIs CONFIGURATION ---
FOOTBALL_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
SPORTRADAR_SOCCER_API = os.getenv("SPORTRADAR_SOCCER_API")

# --- ODDS & BETTING APIs CONFIGURATION ---
THE_ODDS_API_KEY = os.getenv("THE_ODDS_API_KEY")

BETTING_API_KEYS = {
    "bet365": os.getenv("BET365_API_KEY"),
    "bwin": os.getenv("BWIN_API_KEY"),
    "betano": os.getenv("BETANO_API_KEY"),
    "the_odds": THE_ODDS_API_KEY
}

# --- GOOGLE CLOUD CONFIGURATION ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_SA_KEY = os.getenv("GCP_SA_KEY")

# --- LEAGUE MAPPING ---
# Códigos sincronizados para football-data.org V4
LEAGUES = {
    "premier": {"name": "Premier League", "id": "PL"},
    "la_liga": {"name": "La Liga", "id": "PD"},
    "serie_a": {"name": "Serie A", "id": "SA"},
    "bundesliga": {"name": "Bundesliga", "id": "BL1"},
    "champions": {"name": "UEFA Champions League", "id": "CL"},
    "ligue_1": {"name": "Ligue 1", "id": "FL1"}
}

# Alias para compatibilidad
SUPPORTED_LEAGUES = LEAGUES

# --- ML MODEL CONFIG ---
MODEL_PATH = BASE_DIR / "models/xgboost_model.pkl"
SCALER_PATH = BASE_DIR / "models/scaler.pkl"
MODEL_VERSION = "2.0_XGBOOST"
