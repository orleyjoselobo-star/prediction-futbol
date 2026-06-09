"""Configuration settings for the football prediction system synchronized with your environment."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Project Root Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Cloud Run safe paths (Using /tmp for dynamic files to prevent PermissionError)
DATA_DIR = Path("/tmp/data")
MODELS_DIR = BASE_DIR / "models"
LOGS_DIR = Path("/tmp/logs")

# Create required infrastructure directories safely (only if they are in /tmp)
for directory in [DATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- TELEGRAM CONFIGURATION ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# --- GOOGLE CLOUD & FIREBASE CONFIGURATION ---
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_REGION = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")

# --- FOOTBALL API CONFIGURATION ---
FOOTBALL_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY")

# --- BETTING APIs CONFIGURATION ---
BETTING_API_KEYS = {
    "bet365": os.getenv("BET365_API_KEY"),
    "bwin": os.getenv("BWIN_API_KEY"),
    "betano": os.getenv("BETANO_API_KEY")
}

# --- DATABASE CONFIGURATION ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/prediction_futbol")

# --- MACHINE LEARNING MODEL CONFIGURATION ---
MODEL_PATH = BASE_DIR / os.getenv("MODEL_PATH", "models/xgboost_model.pkl")
SCALER_PATH = BASE_DIR / os.getenv("SCALER_PATH", "models/scaler.pkl")
MODEL_VERSION = "2.0_XGBOOST"
MIN_PREDICTION_CONFIDENCE = 0.65

# --- LEAGUE MAPPING & CODES SYNCHRONIZED FOR FOOTBALL-DATA.ORG V4 ---
LEAGUES = {
    "premier": {"name": "Premier League Inglaterra", "id": "PL"},
    "la_liga": {"name": "La Liga España", "id": "PD"},
    "serie_a": {"name": "Serie A Italia", "id": "SA"},
    "bundesliga": {"name": "Bundesliga Alemania", "id": "BL1"},
    "champions": {"name": "UEFA Champions League", "id": "CL"},
    "ligue_1": {"name": "Ligue 1 Francia", "id": "FL1"}
}

SUPPORTED_LEAGUES = LEAGUES

# --- LOGGING CONFIGURATION ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# --- ENVIRONMENT CONFIGURATION ---
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
