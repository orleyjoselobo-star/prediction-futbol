"""
Main application file for Cloud Run deployment.
Integrates Flask web server with the Telegram bot using a robust request isolated event loop.
"""
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.request import HTTPXRequest
from src.config.settings import TELEGRAM_BOT_TOKEN
from src.telegram_bot.handlers import TelegramHandlers, SELECT_LEAGUE, SELECT_MATCH, SHOW_PREDICTION
from src.logger import setup_logger

# Initialize Logger and Flask App
logger = setup_logger(__name__)
app = Flask(__name__)

def build_telegram_application():
    """Factory function to build and configure the Telegram Application instance."""
    token = os.getenv("TELEGRAM_TOKEN") or TELEGRAM_BOT_TOKEN
    
    if not token or token == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_TOKEN no configurado en el entorno de ejecución.")
        return None

    # Configurar cliente HTTP optimizado para Cloud Run
    local_request = HTTPXRequest(
        connection_pool_size=100,
        read_timeout=30.0,
        write_timeout=30.0,
        connect_timeout=30.0,
        pool_timeout=30.0
    )
    
    bot_app = Application.builder().token(token).request(local_request).build()
    handlers = TelegramHandlers()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", handlers.start)],
        states={
            SELECT_LEAGUE: [CallbackQueryHandler(handlers.select_league)],
            SELECT_MATCH: [CallbackQueryHandler(handlers.select_match)],
            SHOW_PREDICTION: [CallbackQueryHandler(handlers.select_league)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel)],
    )
    
    bot_app.add_handler(conv_handler)
    return bot_app

async def process_update_async(json_payload):
    """Asynchronously initializes the app components and processes the incoming update safely."""
    bot_app = build_telegram_application()
    if not bot_app:
        raise RuntimeError("No se pudo construir la aplicacion de Telegram.")
        
    async with bot_app:
        update = Update.de_json(json_payload, bot_app.bot)
        await bot_app.process_update(update)

@app.route("/", methods=["GET"])
def health_check():
    """Basic health check endpoint for Google Cloud Run."""
    return jsonify({"status": "healthy", "service": "football-prediction-bot"}), 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """
    Main webhook endpoint. Processes each request within its own isolated context
    to completely avoid 'Event loop is closed' or multi-threading asyncio issues.
    """
    try:
        json_data = request.get_json(force=True)
        if json_data:
            # Ejecutar de forma aislada y auto-contenida para esta peticion de Cloud Run
            asyncio.run(process_update_async(json_data))
        return "OK", 200
    except Exception as e:
        logger.error(f"Error procesando update en el Webhook: {e}", exc_info=True)
        return "Error Interno", 500

if __name__ == "__main__":
    logger.info("Arrancando servidor en modo local de pruebas...")
    app.run(host="0.0.0.0", port=8080, debug=True)
