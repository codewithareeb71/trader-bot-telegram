import requests
import time
from .config import OANDA_API_KEY, OANDA_BASE_URL

HEADERS = {"Authorization": f"Bearer {OANDA_API_KEY}"}

# =========================
# FETCH CANDLES
# =========================
def fetch_candles(symbol="EUR_USD", count=50, granularity="M1"):
    """
    Fetch candle data from OANDA API
    Returns dict with 'open', 'high', 'low', 'close' lists
    """
    url = f"{OANDA_BASE_URL}/v3/instruments/{symbol}/candles"
    params = {
        "count": count,
        "granularity": granularity,
        "price": "M"  # Mid prices
    }

    for attempt in range(3):
        try:
            res = requests.get(url, headers=HEADERS, params=params, timeout=20)
            res.raise_for_status()
            data = res.json()

            if "candles" not in data:
                return None

            candles = [c for c in data["candles"] if c.get("complete")]
            if len(candles) < 5:
                return None

            return {
                "open": [float(c["mid"]["o"]) for c in candles],
                "high": [float(c["mid"]["h"]) for c in candles],
                "low": [float(c["mid"]["l"]) for c in candles],
                "close": [float(c["mid"]["c"]) for c in candles],
            }

        except Exception as e:
            time.sleep(2)
            if attempt == 2:
                return None

# =========================
# LAST CLOSE PRICE
# =========================
def last_close_price(symbol="EUR_USD"):
    data = fetch_candles(symbol)
    if not data:
        return None
    return data["close"][-1]

# =========================
# TREND CALCULATION
# =========================
def get_trend(symbol="EUR_USD"):
    data = fetch_candles(symbol)
    if not data or len(data["close"]) < 3:
        return {"direction": "UNKNOWN"}

    c = data["close"]
    if c[-1] > c[-2] > c[-3]:
        return {"direction": "bullish"}
    elif c[-1] < c[-2] < c[-3]:
        return {"direction": "bearish"}
    else:
        return {"direction": "sideways"}