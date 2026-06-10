"""Main application file for Cloud Run deployment."""
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from src.telegram_bot.handlers import TelegramHandlers
from src.logger import setup_logger

# Importamos el token de forma segura
from src.config.settings import TELEGRAM_BOT_TOKEN

logger = setup_logger(__name__)
app = Flask(__name__)

# Validación estricta
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
    logger.error("CRÍTICO: Token de Telegram no encontrado en las variables de entorno.")
    raise ValueError("Falta el TELEGRAM_BOT_TOKEN.")

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint básico de salud."""
    return jsonify({"status": "healthy"}), 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Recibe el update y lo procesa con rutas sin estado (Serverless friendly)."""
    try:
        json_data = request.get_json(force=True)

        async def process_update_safely():
            handlers = TelegramHandlers()
            bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
            
            # --- SOLUCIÓN: MANEJADORES DIRECTOS (SIN AMNESIA) ---
            # Enlazamos los botones directamente a sus funciones usando expresiones regulares
            bot_app.add_handler(CommandHandler("start", handlers.start))
            bot_app.add_handler(CallbackQueryHandler(handlers.select_league, pattern='^league_'))
            bot_app.add_handler(CallbackQueryHandler(handlers.select_match, pattern='^match_'))
            bot_app.add_handler(CallbackQueryHandler(handlers.start, pattern='^back_leagues'))
            
            async with bot_app:
                update = Update.de_json(json_data, bot_app.bot)
                await bot_app.process_update(update)

        # Ejecución asíncrona aislada para evitar conflictos de hilos
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_update_safely())
        loop.close()
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Error crítico en webhook: {e}", exc_info=True)
        return "Internal Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
