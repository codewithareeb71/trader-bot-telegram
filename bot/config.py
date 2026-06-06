import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("8904854068:AAGBGmObrS9lTyB625xezlMxE3XcVfc1phI")
OANDA_API_KEY = os.getenv("8a6c035d6b635fd0c642a8b54f6d8342-58fa133093db2d765743e165f63d20a0")
OANDA_BASE_URL = "https://api-fxpractice.oanda.com"