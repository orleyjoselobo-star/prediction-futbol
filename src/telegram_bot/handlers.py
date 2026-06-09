"""Telegram Bot conversation handlers and match selection workflows."""

import asyncio
import pandas as pd
from typing import Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from src.config.settings import LEAGUES
from src.models.predictor import MatchPredictor
from src.logger import setup_logger

# Initialize Logger and Predictor Core
logger = setup_logger(__name__)
predictor = MatchPredictor()

# State definitions for ConversationHandler
SELECT_LEAGUE, SELECT_MATCH, SHOW_PREDICTION = range(3)

def ensure_async_loop():
    """Safely retrieves or registers the correct event loop for the current thread context."""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

class TelegramHandlers:
    """Encapsulates all callback states and response flows for the Telegram interaction."""

    def __init__(self):
        # Mapeo local de códigos internos a nombres legibles de ligas colombianas e internacionales
        self.leagues = LEAGUES

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the conversation and displays available football leagues to the user."""
        ensure_async_loop()
        try:
            logger.info(f"Comando /start recibido de usuario: {update.effective_user.id}")
            
            # Construir botones interactivos basados en la configuración de ligas
            keyboard = []
            for league_id, league_data in self.leagues.items():
                keyboard.append([InlineKeyboardButton(league_data["name"], callback_data=f"league_{league_id}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.message:
                await update.message.reply_text(
                    "⚽ ¡Bienvenido al Bot de Predicciones de Fútbol! ⚽\n\n"
                    "Selecciona una de las siguientes ligas para analizar los próximos partidos:",
                    reply_markup=reply_markup
                )
            elif update.callback_query:
                query = update.callback_query
                await query.answer()
                await query.edit_message_text(
                    "⚽ Selecciona una de las siguientes ligas para analizar los próximos partidos:",
                    reply_markup=reply_markup
                )
                
            return SELECT_LEAGUE

        except Exception as e:
            logger.error(f"Error crítico en el manejador 'start': {e}", exc_info=True)
            if update.message:
                await update.message.reply_text("Ocurrió un error inicializando el menú. Por favor intenta de nuevo.")
            return ConversationHandler.END

    async def select_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles league selection and lists upcoming matches available for inference."""
        ensure_async_loop()
        query = update.callback_query
        await query.answer()
        
        try:
            league_id = query.data.replace("league_", "")
            logger.info(f"Liga seleccionada por usuario: {league_id}")
            
            # Guardar contexto de la liga seleccionada en los datos del usuario
            context.user_data["selected_league"] = league_id
            
            # --- SIMULACIÓN DE PARTIDOS DISPONIBLES ---
            # Reemplaza este diccionario simulado por tu consulta real a base de datos o API de fixtures
            partidos_simulados = {
                "colombia": [
                    {"id": "m1", "home": "Atlético Nacional", "away": "Millonarios"},
                    {"id": "m2", "home": "Junior", "away": "América de Cali"}
                ],
                "premier": [
                    {"id": "m3", "home": "Manchester City", "away": "Arsenal"},
                    {"id": "m4", "home": "Liverpool", "away": "Chelsea"}
                ]
            }
            
            matches = partidos_simulados.get(league_id, [])
            
            if not matches:
                await query.edit_message_text(
                    "⚠️ No hay partidos disponibles o programados para predicción en esta liga actualmente.\n"
                    "Usa /start para volver al menú principal."
                )
                return ConversationHandler.END
                
            # Construir teclado con los partidos de la liga elegida
            keyboard = []
            for match in matches:
                btn_text = f"{match['home']} vs {match['away']}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"match_{match['id']}_{match['home']}_{match['away']}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Volver al menú de ligas", callback_data="back_leagues")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=f"📅 Próximos partidos de la liga seleccionada:\nSelecciona el encuentro que deseas predecir:",
                reply_markup=reply_markup
            )
            return SELECT_MATCH

        except Exception as e:
            logger.error(f"Error crítico en el manejador 'select_league': {e}", exc_info=True)
            await query.edit_message_text("Ocurrió un error al procesar la liga. Usa /start para reiniciar.")
            return ConversationHandler.END

    async def select_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Executes feature assembly, triggers ML prediction, and outputs final report."""
        ensure_async_loop()
        query = update.callback_query
        await query.answer()
        
        try:
            callback_data = query.data
            
            # Opción de navegación hacia atrás
            if callback_data == "back_leagues":
                return await self.start(update, context)
                
            # Extraer metadatos básicos del partido desde el callback_data
            # Formato: match_{id}_{home}_{away}
            parts = callback_data.split("_")
            match_id = parts[1]
            home_team = parts[2]
            away_team = parts[3]
            
            logger.info(f"Ejecutando predicción para encuentro: {home_team} vs {away_team}")
            await query.edit_message_text("🤖 Calculando variables de forma y procesando matrices XGBoost...")

            # --- CONSTRUCCIÓN DE LA MATRIZ DE CARACTERÍSTICAS (MOCK COMPATIBLE) ---
            # Aquí acoplamos un registro base con las columnas que el predictor analítico espera leer.
            feature_data = {
                "form_recent": [0.25],  # Simula diferencia positiva de rendimiento para el local
                "goals_for": [1.5]     # Simula ventaja promedio en goles anotados
            }
            feature_df = pd.DataFrame(feature_data)

            # Ejecutar inferencia a través de nuestro componente centralizado MatchPredictor
            prediction_res = predictor.predict(feature_df)
            
            probs = prediction_res["probabilities"]
            outcome = prediction_res["prediction"]
            
            # Traducir etiqueta técnica a una interfaz amigable
            outcome_text = "Gana Local 🏠"
            if outcome == "DRAW":
                outcome_text = "Empate 🤝"
            elif outcome == "AWAY_WIN":
                outcome_text = "Gana Visitante 🚀"

            # Formatear reporte estructurado para el usuario final en Telegram
            reporte = (
                f"📊 *REPORTE PREDICTIVO INTELIGENTE*\n"
                f"⚔️ *Encuentro:* {home_team} vs {away_team}\n\n"
                f"🔮 *Predicción recomendada:* {outcome_text}\n\n"
                f"📈 *Probabilidades Calculadas:*\n"
                f"• Local 🏠: `{probs['HOME_WIN'] * 100:.1f}%`\n"
                f"• Empate 🤝: `{probs['DRAW'] * 100:.1f}%`\n"
                f"• Visitante 🚀: `{probs['AWAY_WIN'] * 100:.1f}%`\n\n"
                f"_*Nota:* Las probabilidades se calculan de manera paramétrica / ML según variables de forma actual._"
            )

            keyboard = [[InlineKeyboardButton("🔄 Consultar otro partido", callback_data="back_leagues")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(text=reporte, reply_markup=reply_markup, parse_mode="Markdown")
            return ConversationHandler.END

        except Exception as e:
            logger.error(f"Error crítico en el manejador 'select_match': {e}", exc_info=True)
            await query.edit_message_text("❌ Error al calcular la predicción del encuentro. Usa /start para reintentar.")
            return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and terminates the active conversational loop safely."""
        ensure_async_loop()
        logger.info(f"Flujo conversacional cancelado por usuario: {update.effective_user.id}")
        if update.message:
            await update.message.reply_text("Flujo cancelado con éxito. Usa /start cuando desees volver a predecir.")
        elif update.callback_query:
            await update.callback_query.edit_message_text("Flujo cancelado. Usa /start cuando desees volver a predecir.")
        return ConversationHandler.END
