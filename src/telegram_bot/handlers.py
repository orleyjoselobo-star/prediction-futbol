"""Telegram Bot conversation handlers and match selection workflows."""

import asyncio
import pandas as pd
from typing import Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, CommandHandler

from src.config.settings import LEAGUES
from src.models.predictor import MatchPredictor
from src.logger import setup_logger
from src.data.fetcher import FootballDataFetcher

# Initialize Logger and Predictor
logger = setup_logger(__name__)
predictor = MatchPredictor()

# State definitions
SELECT_LEAGUE, SELECT_MATCH, SHOW_PREDICTION = range(3)

def ensure_async_loop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

class TelegramHandlers:
    def __init__(self):
        self.leagues = LEAGUES

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ensure_async_loop()
        keyboard = []
        for league_id, league_data in self.leagues.items():
            keyboard.append([InlineKeyboardButton(league_data["name"], callback_data=f"league_{league_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.message:
            await update.message.reply_text("⚽ Selecciona una liga:", reply_markup=reply_markup)
        return SELECT_LEAGUE

    async def select_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ensure_async_loop()
        query = update.callback_query
        await query.answer()
        
        league_key = query.data.replace("league_", "")
        league_config = self.leagues.get(league_key)
        
        fetcher = FootballDataFetcher()
        data = fetcher.get_league_matches(league_config["id"])
        matches = data.get("matches", [])
        
        if not matches:
            await query.edit_message_text("No hay partidos disponibles.")
            return ConversationHandler.END

        keyboard = []
        for match in matches[:5]:
            home = match['homeTeam']['name'][:10]
            away = match['awayTeam']['name'][:10]
            callback = f"match_{match['id']}_{home}_{away}"
            keyboard.append([InlineKeyboardButton(f"{home} vs {away}", callback_data=callback)])
        
        await query.edit_message_text("Selecciona el partido:", reply_markup=InlineKeyboardMarkup(keyboard))
        return SELECT_MATCH

    async def select_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text("Predicción calculada...")
        return ConversationHandler.END
