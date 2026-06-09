"""Telegram bot message handlers"""

import pandas as pd
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from typing import Optional, List
from src.data.fetcher import FootballDataFetcher
from src.data.processor import DataProcessor
from src.models.predictor import MatchPredictor
from src.api.betting_odds import BettingOddsAPI
from src.config.settings import SUPPORTED_LEAGUES, MIN_PREDICTION_CONFIDENCE
from src.logger import setup_logger
from src.utils.helpers import format_match_info

logger = setup_logger(__name__)

# Conversation states
SELECT_LEAGUE = 0
SELECT_MATCH = 1
SHOW_PREDICTION = 2


class TelegramHandlers:
    """Handle Telegram bot interactions"""

    def __init__(self):
        self.fetcher = FootballDataFetcher()
        self.processor = DataProcessor()
        self.predictor = MatchPredictor()
        self.odds_api = BettingOddsAPI()
        self.matches_cache = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start command handler"""
        try:
            user = update.effective_user
            welcome_message = f"¡Hola {user.first_name}! 👋\n\nBienvenido al bot de predicción de fútbol ⚽\n\nEscoge una liga para ver los partidos del día:"
            
            # Create inline keyboard with leagues using SUPPORTED_LEAGUES safely
            keyboard = []
            fila = []
            for league_key, league_info in SUPPORTED_LEAGUES.items():
                boton = InlineKeyboardButton(
                    f"{league_info['name']} 🌍",
                    callback_data=f"league_{league_key}"
                )
                fila.append(boton)
                if len(fila) == 2:
                    keyboard.append(fila)
                    fila = []
            if fila:
                keyboard.append(fila)
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Dynamic support if coming from /start command or back button
            if update.message:
                await update.message.reply_text(welcome_message, reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(welcome_message, reply_markup=reply_markup)
                
            return SELECT_LEAGUE
        except Exception as e:
            logger.error(f"Error in start handler: {e}")
            if update.message:
                await update.message.reply_text("Ocurrió un error. Por favor intenta de nuevo.")
            return ConversationHandler.END

    async def select_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle league selection"""
        query = update.callback_query
        try:
            await query.answer()
            
            if query.data == "back_to_start":
                return await self.start(update, context)
            
            league_key = query.data.replace("league_", "")
            context.user_data["selected_league"] = league_key
            
            league_info = SUPPORTED_LEAGUES.get(league_key, {})
            
            # Fetch matches for the selected league
            league_code = league_info.get("id")
            matches_data = self.fetcher.get_league_matches(league_code)
            matches = matches_data.get("matches", [])
            
            self.matches_cache[query.from_user.id] = matches
            
            if not matches:
                keyboard = [[InlineKeyboardButton("⬅️ Volver al menú", callback_data="back_to_start")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"No hay partidos disponibles para {league_info.get('name')} hoy.", reply_markup=reply_markup)
                return SELECT_LEAGUE
            
            # Show matches
            message = f"Partidos de {league_info.get('name')} 🏆\n\n"
            keyboard = []
            
            for idx, match in enumerate(matches[:10]):  # Limit to 10 matches
                home_team = match.get("homeTeam", {}).get("name", "Unknown")
                away_team = match.get("awayTeam", {}).get("name", "Unknown")
                match_time = match.get("utcDate", "TBD").split("T")[1][:5] if "T" in match.get("utcDate", "") else "TBD"
                
                message += f"{idx + 1}. {home_team} vs {away_team} - {match_time}\n"
                keyboard.append([
                    InlineKeyboardButton(
                        f"{home_team} vs {away_team}",
                        callback_data=f"match_{idx}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("⬅️ Volver al menú", callback_data="back_to_start")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(message, reply_markup=reply_markup)
            return SELECT_MATCH
        except Exception as e:
            logger.error(f"Error in select_league handler: {e}")
            if query:
                await query.edit_message_text("Ocurrió un error. Por favor intenta de nuevo.")
            return SELECT_LEAGUE

    async def select_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle match selection and show prediction"""
        query = update.callback_query
        try:
            await query.answer()
            
            if query.data == "back_to_start":
                return await self.start(update, context)
            
            match_idx = int(query.data.replace("match_", ""))
            user_id = query.from_user.id
            
            matches = self.matches_cache.get(user_id, [])
            if match_idx >= len(matches):
                await query.edit_message_text("Partido no encontrado.")
                return SELECT_MATCH
            
            match = matches[match_idx]
            context.user_data["selected_match"] = match
            
            # Extract match info
            home_team = match.get("homeTeam", {})
            away_team = match.get("awayTeam", {})
            match_time = match.get("utcDate", "TBD")
            
            # Get prediction
            home_features = self.processor.calculate_team_features(pd.DataFrame(), home_team.get("name", ""))
            away_features = self.processor.calculate_team_features(pd.DataFrame(), away_team.get("name", ""))
            
            X = self.processor.prepare_features_for_prediction(home_features, away_features)
            prediction = self.predictor.predict(X)
            
            # Get odds
            odds = self.odds_api.compare_best_odds(str(match.get("id", "")))
            
            # Format message
            message = f"📊 Predicción: {home_team.get('name')} vs {away_team.get('name')}\n\n"
            message += f"🕐 Hora: {match_time}\n\n"
            message += f"🤖 Predicción del modelo:\n"
            
            probs = prediction.get("probabilities", {})
            message += f"Victoria local: {probs.get('HOME_WIN', 0)*100:.1f}%\n"
            message += f"Empate: {probs.get('DRAW', 0)*100:.1f}%\n"
            message += f"Victoria visitante: {probs.get('AWAY_WIN', 0)*100:.1f}%\n\n"
            
            message += f"💰 Mejores cuotas:\n"
            if "home_win" in odds:
                message += f"Victoria local: {odds['home_win'].get('odds', 'N/A')} ({odds['home_win'].get('bookmaker', 'N/A')})\n"
            if "draw" in odds:
                message += f"Empate: {odds['draw'].get('odds', 'N/A')} ({odds['draw'].get('bookmaker', 'N/A')})\n"
            if "away_win" in odds:
                message += f"Victoria visitante: {odds['away_win'].get('odds', 'N/A')} ({odds['away_win'].get('bookmaker', 'N/A')})\n"
            
            # Return button for final view
            keyboard = [[InlineKeyboardButton("🔄 Consultar otra liga / partido", callback_data="back_to_start")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup)
            return SHOW_PREDICTION
        except Exception as e:
            logger.error(f"Error in select_match handler: {e}")
            if query:
                await query.edit_message_text("Ocurrió un error al obtener la predicción.")
            return SELECT_MATCH

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel command handler"""
        await update.message.reply_text("Operación cancelada. Escribe /start para comenzar de nuevo.")
        return ConversationHandler.END
