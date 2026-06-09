async def select_league(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handles league selection and calls the API to list matches."""
        ensure_async_loop()
        query = update.callback_query
        await query.answer()
        
        try:
            league_key = query.data.replace("league_", "")
            logger.info(f"Liga seleccionada: {league_key}")
            
            # Importar el fetcher dentro de la función o al inicio del archivo
            from src.data.fetcher import FootballDataFetcher
            
            # Obtener el ID de la liga desde tu configuración en settings.py
            league_config = self.leagues.get(league_key)
            if not league_config:
                await query.edit_message_text("Error: Liga no encontrada.")
                return ConversationHandler.END
            
            # Llamar a la API real
            fetcher = FootballDataFetcher()
            # Asumimos que get_league_matches devuelve una lista de dicts
            data = fetcher.get_league_matches(league_config["id"])
            matches = data.get("matches", [])
            
            if not matches:
                await query.edit_message_text(
                    f"⚠️ No hay partidos disponibles para {league_config['name']} en este momento.\n"
                    "Usa /start para probar otra liga."
                )
                return ConversationHandler.END
                
            # Construir teclado dinámico con partidos reales
            keyboard = []
            for match in matches[:6]: # Mostramos hasta 6 partidos
                # Limpiamos nombres para el callback
                home = match['homeTeam']['name'][:10]
                away = match['awayTeam']['name'][:10]
                btn_text = f"{home} vs {away}"
                callback = f"match_{match['id']}_{home}_{away}"
                keyboard.append([InlineKeyboardButton(btn_text, callback_data=callback)])
            
            keyboard.append([InlineKeyboardButton("🔙 Volver", callback_data="back_leagues")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=f"📅 Partidos próximos en {league_config['name']}:",
                reply_markup=reply_markup
            )
            return SELECT_MATCH

        except Exception as e:
            logger.error(f"Error conectando a la API: {e}", exc_info=True)
            await query.edit_message_text("❌ Error al obtener datos de la liga. Intenta de nuevo más tarde.")
            return ConversationHandler.END
