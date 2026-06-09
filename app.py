"""Main application file for Cloud Run deployment."""
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler
from src.telegram_bot.handlers import TelegramHandlers, SELECT_LEAGUE, SELECT_MATCH
from src.logger import setup_logger

logger = setup_logger(__name__)
app = Flask(__name__)

# Configuración global del bot (persiste en memoria del contenedor)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
handlers = TelegramHandlers()

def get_bot_app():
    """Crea la instancia de la aplicación de Telegram."""
    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", handlers.start)],
        states={
            SELECT_LEAGUE: [CallbackQueryHandler(handlers.select_league, pattern='^league_')],
            SELECT_MATCH: [CallbackQueryHandler(handlers.select_match, pattern='^match_')],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel)],
        per_message=False
    )
    bot_app.add_handler(conv_handler)
    return bot_app

# Instancia global para evitar recrearla en cada request
bot_app = get_bot_app()

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    """Procesa el webhook usando la instancia global."""
    try:
        json_data = request.get_json(force=True)
        # Ejecutar asíncronamente en el loop actual del proceso
        asyncio.run(bot_app.process_update(Update.de_json(json_data, bot_app.bot)))
        return "OK", 200
    except Exception as e:
        logger.error(f"Error en webhook: {e}", exc_info=True)
        return "Error", 500

if __name__ == "__main__":
    # Esto solo corre localmente
    app.run(host="0.0.0.0", port=8080)
