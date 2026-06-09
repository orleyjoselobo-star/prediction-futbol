import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler
from src.telegram_bot.handlers import TelegramHandlers, SELECT_LEAGUE, SELECT_MATCH
from src.logger import setup_logger

logger = setup_logger(__name__)
app = Flask(__name__)

# Configuración global
TOKEN = os.getenv("TELEGRAM_TOKEN")
handlers = TelegramHandlers()

# Construimos la app de Telegram fuera de las rutas
bot_app = ApplicationBuilder().token(TOKEN).build()
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

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Recibe el update y lo procesa de forma síncrona para Cloud Run."""
    json_data = request.get_json(force=True)
    
    # IMPORTANTE: No usamos asyncio.run() aquí. 
    # Usamos el loop existente del proceso para procesar el update.
    try:
        update = Update.de_json(json_data, bot_app.bot)
        # Esto asegura que el proceso se mantenga vivo sin crear loops conflictivos
        asyncio.get_event_loop().run_until_complete(bot_app.process_update(update))
        return "OK", 200
    except Exception as e:
        logger.error(f"Error crítico en webhook: {e}")
        return "Internal Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
