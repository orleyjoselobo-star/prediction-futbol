"""
Main application file for Cloud Run deployment.
Integrates Flask web server with the Telegram bot using your project layout.
"""
import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler
from src.config.settings import TELEGRAM_BOT_TOKEN
from src.telegram_bot.handlers import TelegramHandlers, SELECT_LEAGUE, SELECT_MATCH, SHOW_PREDICTION
from src.logger import setup_logger

# Initialize Logger and Flask App
logger = setup_logger(__name__)
app = Flask(__name__)

# Global Telegram Application instance
telegram_app = None

async def init_telegram_bot():
    """Initializes the Telegram application instance and hooks handlers."""
    global telegram_app
    # Leer el token desde tu .env real (TELEGRAM_TOKEN) o el fallback de configuración
    token = os.getenv("TELEGRAM_TOKEN") or TELEGRAM_BOT_TOKEN
    
    if not token or token == "your_telegram_bot_token_here":
        logger.error("TELEGRAM_TOKEN no configurado en el entorno de ejecución.")
        return None

    logger.info("Inicializando instancia global del Bot de Telegram...")
    
    # Construir la aplicación del bot
    bot_app = Application.builder().token(token).build()
    
    # Instanciar los manejadores conversacionales
    handlers = TelegramHandlers()
    
    # Estructura de la máquina de estados conversacional
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
    
    # Inicializar componentes internos de python-telegram-bot sin arrancar polling
    await bot_app.initialize()
    logger.info("Instancia de Telegram configurada e inicializada con éxito.")
    return bot_app

def safe_get_loop():
    """Safely retrieves the running event loop or sets up a new one."""
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

# Inicialización inicial controlada
loop = safe_get_loop()

if os.getenv("ENVIRONMENT") == "production":
    telegram_app = loop.run_until_complete(init_telegram_bot())

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint básico para que Google Cloud Run verifique que el contenedor está vivo."""
    return jsonify({"status": "healthy", "service": "football-prediction-bot"}), 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    """
    Endpoint principal que recibe las notificaciones en tiempo real desde los servidores 
    de Telegram y las procesa dentro del contenedor de Cloud Run.
    """
    global telegram_app
    current_loop = safe_get_loop()

    if not telegram_app:
        # Inicialización perezosa (lazy initialization) usando el ciclo seguro actual sin romperlo
        logger.info("Ejecutando inicialización tardía en webhook...")
        telegram_app = current_loop.run_until_complete(init_telegram_bot())
        if not telegram_app:
            return "Bot no inicializado", 500

    try:
        # Obtener el payload JSON enviado por Telegram
        json_data = request.get_json(force=True)
        if json_data:
            # Convertir el JSON crudo en un objeto Update entendible por la librería
            update = Update.de_json(json_data, telegram_app.bot)
            
            # Procesar la actualización compartiendo el ciclo de eventos de forma nativa y estable
            current_loop.run_until_complete(telegram_app.process_update(update))
            
        return "OK", 200
    except Exception as e:
        logger.error(f"Error procesando update en el Webhook: {e}", exc_info=True)
        return "Error Interno", 500

if __name__ == "__main__":
    # Modo de ejecución local para pruebas de desarrollo
    logger.info("Arrancando servidor en modo local de pruebas...")
    token_check = os.getenv("TELEGRAM_TOKEN")
    
    if not token_check or token_check == "your_telegram_bot_token_here":
        logger.warning("⚠️ No has configurado tu TELEGRAM_TOKEN en el entorno local.")
        
    app.run(host="0.0.0.0", port=8080, debug=True)
