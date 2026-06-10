"""Main application file for Cloud Run deployment."""
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ConversationHandler
from src.telegram_bot.handlers import TelegramHandlers, SELECT_LEAGUE, SELECT_MATCH
from src.logger import setup_logger

# Importamos el token de forma segura desde tus configuraciones
from src.config.settings import TELEGRAM_BOT_TOKEN

logger = setup_logger(__name__)
app = Flask(__name__)

# Configuración global
handlers = TelegramHandlers()

# Validación estricta para evitar caídas del contenedor
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
    logger.error("CRÍTICO: Token de Telegram no encontrado en las variables de entorno.")
    raise ValueError("Falta el TELEGRAM_BOT_TOKEN. Verifica la configuración de Cloud Run.")

# Construimos la app de Telegram de forma persistente
bot_app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
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

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint básico para que Google Cloud Run verifique que el servicio vive."""
    return jsonify({"status": "healthy"}), 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """Recibe el update y lo procesa creando un loop seguro para el hilo actual."""
    try:
        json_data = request.get_json(force=True)
        update = Update.de_json(json_data, bot_app.bot)
        
        # --- SOLUCIÓN AL ERROR DE HILOS ---
        # 1. Creamos un loop completamente nuevo y aislado para este hilo de Flask
        loop = asyncio.new_event_loop()
        
        # 2. Lo establecemos como el loop principal de este hilo
        asyncio.set_event_loop(loop)
        
        # 3. Ejecutamos la tarea asíncrona hasta que termine
        loop.run_until_complete(bot_app.process_update(update))
        
        # 4. Cerramos el loop para liberar la memoria del contenedor
        loop.close()
        # ----------------------------------
        
        return "OK", 200
    except Exception as e:
        logger.error(f"Error crítico en webhook: {e}", exc_info=True)
        return "Internal Error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
