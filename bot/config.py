import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_BASE_URL = "https://api-fxpractice.oanda.com"

DEFAULT_SYMBOL = "EUR_USD"
GRANULARITY = "M1"