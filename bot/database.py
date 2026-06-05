# database.py
# Stub for future DB integration (SQLite, PostgreSQL, etc.)
import sqlite3

DB_PATH = "bot.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  symbol TEXT, direction TEXT,
                  price REAL, entry TEXT, expiry TEXT,
                  result TEXT, confidence REAL)''')
    conn.commit()
    conn.close()

def insert_trade(symbol, direction, price, entry, expiry, result, confidence):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO trades (symbol,direction,price,entry,expiry,result,confidence) VALUES (?,?,?,?,?,?,?)",
              (symbol,direction,price,entry,expiry,result,confidence))
    conn.commit()
    conn.close()