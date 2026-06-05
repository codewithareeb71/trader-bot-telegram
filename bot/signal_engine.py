from dataclasses import dataclass
from datetime import datetime, timedelta
from .market_data import last_price, trend

@dataclass
class Signal:
    symbol: str
    direction: str
    confidence: float
    price: float
    entry: str
    expiry: str
    trend: str


def generate_signal(symbol):
    price = last_price(symbol)
    tr = trend(symbol)

    if not price:
        return None

    now = datetime.utcnow()

    if tr == "BULLISH":
        direction = "BUY"
    elif tr == "BEARISH":
        direction = "SELL"
    else:
        return None

    return Signal(
        symbol=symbol,
        direction=direction,
        confidence=round(75 + (price % 10), 2),
        price=price,
        entry=now.strftime("%H:%M UTC"),
        expiry=(now + timedelta(minutes=2)).strftime("%H:%M UTC"),
        trend=tr
    )