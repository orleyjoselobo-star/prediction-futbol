"""Telegram Bot conversation handlers and dynamic feature calculation."""

import asyncio
import pandas as pd
from typing import Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.config.settings import LEAGUES
from src.models.predictor import MatchPredictor
from src.logger import setup_logger
from src.data.fetcher import FootballDataFetcher

logger = setup_logger(__name__)
predictor = MatchPredictor()

class TelegramHandlers:
    def __init__(self):
        self.leagues = LEAGUES

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Muestra el menú principal de ligas."""
        keyboard = []
        for league_id, league_data in self.leagues.items():
            keyboard.append([InlineKeyboardButton(league_data["name"], callback_data=f"league_{league_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = "⚽ ¡Bienvenido! Selecciona una liga para analizar:"
        
        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    async def select_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Busca partidos, calcula estadísticas reales y prepara los botones dinámicos."""
        query = update.callback_query
        await query.answer()
        
        league_key = query.data.replace("league_", "")
        league_config = self.leagues.get(league_key)
        
        try:
            fetcher = FootballDataFetcher()
            # 1. Obtener partidos y posiciones reales de la API
            data = fetcher.get_league_matches(league_config["id"])
            matches = data.get("matches", [])
            standings_data = fetcher.get_league_standings(league_config["id"])
            
            if not matches:
                keyboard = [[InlineKeyboardButton("🔙 Volver al menú", callback_data="back_leagues")]]
                await query.edit_message_text(
                    f"⚠️ No hay partidos disponibles en {league_config['name']} en este momento.",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                return

            # 2. Mapear las estadísticas de todos los equipos en un diccionario rápido
            team_stats = {}
            if standings_data and "standings" in standings_data and len(standings_data["standings"]) > 0:
                for row in standings_data["standings"][0].get("table", []):
                    team_stats[row["team"]["id"]] = row

            def calculate_form_score(form_str):
                """Convierte la racha W,D,L en un número de rendimiento."""
                if not form_str or not isinstance(form_str, str): return 0.5
                matches_list = form_str.split(",")
                if not matches_list: return 0.5
                score = sum(3 if r.strip()=='W' else 1 if r.strip()=='D' else 0 for r in matches_list)
                return score / (len(matches_list) * 3)

            keyboard = []
            for match in matches[:6]:
                home_team = match['homeTeam']
                away_team = match['awayTeam']
                
                # 3. EXTRAER DATOS REALES PARA EL XGBOOST
                home_row = team_stats.get(home_team['id'], {})
                away_row = team_stats.get(away_team['id'], {})
                
                # Diferencia de Racha (form_recent)
                home_form = calculate_form_score(home_row.get("form", ""))
                away_form = calculate_form_score(away_row.get("form", ""))
                form_recent = round(home_form - away_form, 2)
                
                # Promedio Goles (goals_for)
                played = home_row.get("playedGames", 1) or 1
                goals = home_row.get("goalsFor", 1) or 1
                goals_for = round(goals / played, 2)

                # 4. Formatear nombres y fechas
                home_name = home_team['name'][:11].replace("_", " ")
                away_name = away_team['name'][:11].replace("_", " ")
                raw_date = match.get('utcDate', '')
                match_date = "Pendiente"
                if raw_date:
                    try:
                        y, m, d = raw_date.split('T')[0].split('-')
                        match_date = f"{d}-{m}-{y}"
                    except: pass

                # 5. INYECTAR LA MATEMÁTICA EN EL BOTÓN
                callback = f"match_{home_name}_{away_name}_{match_date}_{form_recent}_{goals_for}"
                keyboard.append([InlineKeyboardButton(f"{home_name} vs {away_name}", callback_data=callback)])
            
            keyboard.append([InlineKeyboardButton("🔙 Volver al menú", callback_data="back_leagues")])
            await query.edit_message_text("Selecciona el partido que deseas analizar:", reply_markup=InlineKeyboardMarkup(keyboard))
            
        except Exception as e:
            logger.error(f"Error en select_league: {e}", exc_info=True)
            await query.edit_message_text("❌ Error al conectarse con la API de fútbol.")

    async def select_match(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Recibe los datos reales del botón y ejecuta el modelo de Machine Learning."""
        query = update.callback_query
        await query.answer()
        
        try:
            parts = query.data.split("_")
            
            # Soporte de compatibilidad para evitar fallos si oprimes botones antiguos del chat
            if len(parts) >= 6:
                home_team = parts[1]
                away_team = parts[2]
                match_date = parts[3].replace("-", "/")
                form_recent = float(parts[4])
                goals_for = float(parts[5])
            else:
                home_team = parts[2] if len(parts) > 2 else "Local"
                away_team = parts[3] if len(parts) > 3 else "Visitante"
                match_date = "Por definir"
                form_recent, goals_for = 0.0, 1.0

            await query.edit_message_text(f"🤖 Analizando datos reales de {home_team} vs {away_team}...")

            # --- INFERENCIA CON DATOS 100% REALES ---
            feature_data = pd.DataFrame({"form_recent": [form_recent], "goals_for": [goals_for]})
            prediction_res = predictor.predict(feature_data)
            probs = prediction_res["probabilities"]
            outcome = prediction_res["prediction"]

            if outcome == "HOME_WIN":
                resultado_texto = f"Gana {home_team} 🏠"
            elif outcome == "DRAW":
                resultado_texto = "Empate 🤝"
            else:
                resultado_texto = f"Gana {away_team} 🚀"

            reporte = (
                f"📊 <b>REPORTE PREDICTIVO (Datos Reales)</b>\n"
                f"📅 <b>Fecha:</b> {match_date}\n"
                f"⚔️ {home_team} vs {away_team}\n\n"
                f"🔮 <b>Predicción XGBoost:</b> {resultado_texto}\n\n"
                f"📈 <b>Probabilidades:</b>\n"
                f"• Local ({home_team}): <code>{probs.get('HOME_WIN', 0)*100:.1f}%</code>\n"
                f"• Empate: <code>{probs.get('DRAW', 0)*100:.1f}%</code>\n"
                f"• Visitante ({away_team}): <code>{probs.get('AWAY_WIN', 0)*100:.1f}%</code>"
            )
            
            keyboard = [[InlineKeyboardButton("🔙 Volver al menú", callback_data="back_leagues")]]
            await query.edit_message_text(text=reporte, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
            
        except Exception as e:
            logger.error(f"Error crítico en select_match: {e}", exc_info=True)
            await query.edit_message_text("❌ Error al procesar los datos del partido.")

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        text = "Operación cancelada. Usa /start para volver a empezar."
        if update.message:
            await update.message.reply_text(text)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text)
