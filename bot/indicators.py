# indicators.py
# Placeholder for technical indicators
def sma(data, period=14):
    if not data or len(data) < period:
        return None
    return sum(data[-period:]) / period

def ema(data, period=14):
    if not data or len(data) < period:
        return None
    k = 2 / (period + 1)
    ema_val = data[0]
    for price in data[1:]:
        ema_val = price * k + ema_val * (1 - k)
    return ema_val