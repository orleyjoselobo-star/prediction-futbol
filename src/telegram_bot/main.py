"""Main Telegram bot entry point"""

import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, filters
from src.config import TELEGRAM_TOKEN
from src.telegram_bot.handlers import TelegramHandlers, SELECT_LEAGUE, SELECT_MATCH, SHOW_PREDICTION
from src.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Start the Telegram bot"""
    try:
        if not TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN not found in environment variables")
        
        logger.info("Starting Telegram bot...")
        
        # Create application
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Initialize handlers
        handlers = TelegramHandlers()
        
        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", handlers.start)],
            states={
                SELECT_LEAGUE: [CallbackQueryHandler(handlers.select_league)],
                SELECT_MATCH: [CallbackQueryHandler(handlers.select_match)],
                SHOW_PREDICTION: [CallbackQueryHandler(handlers.select_league)],
            },
            fallbacks=[CommandHandler("cancel", handlers.cancel)],
        )
        
        application.add_handler(conv_handler)
        
        logger.info("Bot started successfully. Listening for messages...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise


if __name__ == "__main__":
    main()
