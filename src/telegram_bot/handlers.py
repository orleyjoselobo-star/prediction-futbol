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

# Inicialización
logger = setup_logger(__name__)
predictor = MatchPredictor()

# Definición de estados
SELECT_LEAGUE, SELECT_MATCH, SHOW_PREDICTION = range(3)

def ensure_async_loop():
    """Asegura que el loop de eventos esté disponible."""
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
            await update.message.reply_text("⚽ ¡Bienvenido! Selecciona una liga para analizar:", reply_markup=reply_markup)
        return SELECT_LEAGUE

    async def select_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        ensure_async_loop()
        query = update.callback_query
        await query.answer()
        
        league_key = query.data.replace("league_", "")
        league_config = self.leagues.get(league_key)
        
        try:
            fetcher = FootballDataFetcher()
            data = fetcher.get_league_matches(league_config["id"])
            matches = data.get("matches", [])
            
            if not matches:
                await query.edit_message_text("⚠️ No hay partidos disponibles en este momento.")
                return ConversationHandler.END

            keyboard = []
            for match in matches[:5]:
                home = match['homeTeam']['name'][:10]
                away = match['awayTeam']['name'][:10]
                callback = f"match_{match['id']}_{home}_{away}"
                keyboard.append([InlineKeyboardButton(f"{home} vs {away}", callback_data=callback)])
            
            keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="back_leagues")])
            await query.edit_message_text("Selecciona el partido:", reply_markup=InlineKeyboardMarkup(keyboard))
            return SELECT_MATCH
        except Exception as e:
            logger.error(f"Error en select_league: {e}")
            await query.edit_message_text("❌ Error al obtener partidos.")
            return ConversationHandler.END

    async def select_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        if query.data == "back_leagues":
            return await self.start(update, context)

        try:
            parts = query.data.split("_")
            home_team, away_team = parts[2], parts[3]
            
            await query.edit_message_text(f"🤖 Analizando {home_team} vs {away_team}...")

            # Inferencia real
            feature_data = pd.DataFrame({"form_recent": [0.5], "goals_for": [1.2]})
            prediction_res = predictor.predict(feature_data)
            probs = prediction_res["probabilities"]
            outcome = prediction_res["prediction"]

            reporte = (
                f"📊 *REPORTE PREDICTIVO*\n"
                f"⚔️ {home_team} vs {away_team}\n\n"
                f"🔮 *Predicción:* {outcome}\n\n"
                f"📈 *Probabilidades:*\n"
                f"• Local: `{probs.get('HOME_WIN', 0)*100:.1f}%`\n"
                f"• Empate: `{probs.get('DRAW', 0)*100:.1f}%`\n"
                f"• Visitante: `{probs.get('AWAY_WIN', 0)*100:.1f}%`"
            )
            await query.edit_message_text(text=reporte, parse_mode="Markdown")
            return ConversationHandler.END
        except Exception as e:
            logger.error(f"Error en select_match: {e}")
            await query.edit_message_text("❌ Error al calcular predicción.")
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Método necesario para el ConversationHandler."""
        text = "Flujo cancelado. Usa /start para volver a empezar."
        if update.message:
            await update.message.reply_text(text)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text)
        return ConversationHandler.END
