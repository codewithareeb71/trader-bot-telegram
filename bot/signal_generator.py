# signal_generator.py
# Optional advanced signal generator
from .signal_engine import generate_signal

def advanced_signal(symbol):
    sig = generate_signal(symbol)
    if sig and sig.confidence > 0.6:
        return sig
    return None