from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from .market_data import last_close_price, get_trend
from .logger import logger

@dataclass
class TradeSignal:
    symbol: str
    direction: str
    status: str
    entry_time: str
    expiry_time: str
    confidence: float
    price: float
    trend: str
    message: str
    next_signal: str

def generate_signal(symbol: str) -> Optional[TradeSignal]:
    try:
        price = last_close_price(symbol)
        trend = get_trend(symbol)
        now = datetime.utcnow()

        if not price:
            return None

        direction_raw = trend.get("direction", "unknown")

        if direction_raw == "bullish":
            direction = "BUY"
        elif direction_raw == "bearish":
            direction = "SELL"
        else:
            return None

        # 🔥 ENTRY FIX (25 sec delay like real trading apps)
        entry_dt = now + timedelta(seconds=25)
        expiry_dt = entry_dt + timedelta(minutes=1)

        confidence = 0.75

        return TradeSignal(
            symbol=symbol,
            direction=direction,
            status="ACTIVE",
            entry_time=entry_dt.strftime("%H:%M:%S UTC"),
            expiry_time=expiry_dt.strftime("%H:%M:%S UTC"),
            confidence=confidence,
            price=float(price),
            trend=direction_raw,
            message="signal ready",
            next_signal=(now + timedelta(minutes=1)).strftime("%H:%M UTC")
        )

    except Exception as e:
        logger.error(e)
        return None