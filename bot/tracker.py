# tracker.py
# Placeholder for tracking trade performance
TRADE_LOG = []

def log_trade(symbol, direction, price, result):
    TRADE_LOG.append({
        "symbol": symbol,
        "direction": direction,
        "price": price,
        "result": result
    })

def get_stats():
    return {
        "total_trades": len(TRADE_LOG),
        "wins": sum(1 for t in TRADE_LOG if t["result"]=="WIN"),
        "losses": sum(1 for t in TRADE_LOG if t["result"]=="LOSS")
    }