from dataclasses import dataclass
from datetime import datetime, timedelta
from .market_data import last_close_price, get_trend

@dataclass
class Signal:
    symbol: str
    direction: str        # BUY / SELL / NEUTRAL
    confidence: float
    price: float
    entry: str
    expiry: str
    trend: str

# =========================
# GENERATE SIGNAL
# =========================
def generate_signal(symbol: str, trade_window_minutes: int = 2) -> Signal:
    price = last_close_price(symbol)
    trend_data = get_trend(symbol)
    now = datetime.utcnow()

    if not price or trend_data["direction"] == "UNKNOWN":
        return None

    direction = "NEUTRAL"
    if trend_data["direction"] == "BULLISH":
        direction = "BUY"
    elif trend_data["direction"] == "BEARISH":
        direction = "SELL"

    confidence = round(70 + (price % 10), 2)  # dynamic confidence, 70-79
    entry_time = now.strftime("%H:%M UTC")
    expiry_time = (now + timedelta(minutes=trade_window_minutes)).strftime("%H:%M UTC")

    return Signal(
        symbol=symbol,
        direction=direction,
        confidence=confidence,
        price=price,
        entry=entry_time,
        expiry=expiry_time,
        trend=trend_data["direction"]
    )