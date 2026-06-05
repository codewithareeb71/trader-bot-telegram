# main.py
from bot.telegram_bot import run_bot
from bot.database import init_db
from bot.logger import logger

def main():
    try:
        # Initialize database (safe even if unused)
        init_db()

        logger.info("Starting Trading Bot...")

        # Start Telegram Bot
        run_bot()

    except Exception as e:
        logger.error(f"Fatal error while starting bot: {e}")

if __name__ == "__main__":
    main()