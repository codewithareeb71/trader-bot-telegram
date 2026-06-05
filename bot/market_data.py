import requests
import time
from .config import OANDA_API_KEY, OANDA_BASE_URL

HEADERS = {
    "Authorization": f"Bearer {OANDA_API_KEY}"
}

# =========================
# SAFE CANDLE FETCH
# =========================
def fetch_candles(symbol="EUR_USD", count=50, granularity="M1"):
    if not OANDA_API_KEY:
        return None

    url = f"{OANDA_BASE_URL}/v3/instruments/{symbol}/candles"

    params = {
        "count": count,
        "granularity": granularity,
        "price": "M"
    }

    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=15)
            data = r.json()

            if "candles" not in data:
                return None

            candles = [c for c in data["candles"] if c.get("complete")]

            if len(candles) < 5:
                return None

            return [float(c["mid"]["c"]) for c in candles]

        except Exception:
            time.sleep(1)

    return None


# =========================
# PRICE SAFE
# =========================
def last_close_price(symbol="EUR_USD"):
    data = fetch_candles(symbol)
    if not data:
        return 0.0
    return data[-1]


# =========================
# TREND SAFE
# =========================
def get_trend(symbol="EUR_USD"):
    data = fetch_candles(symbol)

    if not data or len(data) < 3:
        return {"direction": "UNKNOWN"}

    if data[-1] > data[-2] > data[-3]:
        return {"direction": "bullish"}

    if data[-1] < data[-2] < data[-3]:
        return {"direction": "bearish"}

    return {"direction": "sideways"}