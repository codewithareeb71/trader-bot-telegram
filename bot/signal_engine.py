from dataclasses import dataclass
from datetime import datetime, timedelta
from bot.market_data import last_close_price, get_trend

@dataclass
class Signal:
    symbol: str
    direction: str
    confidence: float
    price: float
    entry: str
    expiry: str
    trend: str


def generate_signal(symbol: str, trade_window_minutes: int = 2):
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

    if direction == "NEUTRAL":
        return None

    confidence = round(70 + (price % 10), 2)

    return Signal(
        symbol=symbol,
        direction=direction,
        confidence=confidence,
        price=price,
        entry=now.strftime("%H:%M UTC"),
        expiry=(now + timedelta(minutes=trade_window_minutes)).strftime("%H:%M UTC"),
        trend=trend_data["direction"]
    )