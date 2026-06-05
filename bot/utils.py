# utils.py
# Helper functions
from datetime import datetime

def utc_now():
    return datetime.utcnow()

def format_time(dt: datetime, fmt="%H:%M:%S UTC"):
    return dt.strftime(fmt)