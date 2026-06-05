import os
from dotenv import load_dotenv

load_dotenv()

# =========================
# REQUIRED SECRETS (SAFE)
# =========================

TELEGRAM_BOT_TOKEN = os.getenv("8904854068:AAGBGmObrS9lTyB625xezlMxE3XcVfc1phI")
OANDA_API_KEY = os.getenv("8a6c035d6b635fd0c642a8b54f6d8342-58fa133093db2d765743e165f63d20a0")

# =========================
# DEFAULT SETTINGS
# =========================
OANDA_BASE_URL = os.getenv(
    "OANDA_BASE_URL",
    "https://api-fxpractice.oanda.com"
)

DEFAULT_SYMBOL = "EUR_USD"
GRANULARITY = "M1"


# =========================
# SAFETY CHECK (IMPORTANT)
# =========================
if not TELEGRAM_BOT_TOKEN:
    raise Exception("❌ TELEGRAM_BOT_TOKEN missing in environment")

if not OANDA_API_KEY:
    raise Exception("❌ OANDA_API_KEY missing in environment")