import requests
import time
from .config import OANDA_API_KEY, OANDA_BASE_URL

HEADERS = {"Authorization": f"Bearer {OANDA_API_KEY}"}


def fetch_candles(symbol="EUR_USD"):
    url = f"{OANDA_BASE_URL}/v3/instruments/{symbol}/candles"
    params = {"count": 50, "granularity": "M1", "price": "M"}

    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=20)
            data = r.json()

            if "candles" not in data:
                return None

            candles = [c for c in data["candles"] if c.get("complete")]

            if len(candles) < 5:
                return None

            return [float(c["mid"]["c"]) for c in candles]

        except:
            time.sleep(2)

    return None


def last_close_price(symbol="EUR_USD"):
    data = fetch_candles(symbol)
    return data[-1] if data else None


def get_trend(symbol="EUR_USD"):
    data = fetch_candles(symbol)

    if not data or len(data) < 3:
        return {"direction": "UNKNOWN"}

    if data[-1] > data[-2] > data[-3]:
        return {"direction": "bullish"}
    elif data[-1] < data[-2] < data[-3]:
        return {"direction": "bearish"}
    else:
        return {"direction": "sideways"}