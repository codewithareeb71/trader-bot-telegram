# strategy_engine.py
# Placeholder for multi-strategy evaluation
def evaluate_strategy(symbol, data):
    # Example: basic rule
    last_price = data[-1] if data else 0
    if last_price > 1.2:
        return "BUY"
    elif last_price < 1.0:
        return "SELL"
    return "HOLD"