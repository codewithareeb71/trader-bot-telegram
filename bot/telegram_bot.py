from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime

from .config import TELEGRAM_BOT_TOKEN
from .signal_engine import generate_signal

# =========================
# CONFIG
# =========================
CURRENCY_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD",
    "USD_CAD", "NZD_USD", "EUR_GBP", "GBP_JPY", "USD_TRY"
]

MAX_TRADES_PER_DAY = 10
TRADE_RESET_MINUTES = 30  # 30 min rest after max trades

trade_counter = {
    "count": 0,
    "date": datetime.utcnow().date(),
    "last_reset": datetime.utcnow()
}

# =========================
# APP SETUP
# =========================
def create_app():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    return app

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trade_counter["count"] = 0
    trade_counter["date"] = datetime.utcnow().date()
    trade_counter["last_reset"] = datetime.utcnow()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])

    await update.message.reply_text(
        "🚀 TRADING BOT READY\n\n"
        f"⚡ Max Trades/Day: {MAX_TRADES_PER_DAY}\n"
        "📌 Click below to get a trade signal",
        reply_markup=keyboard
    )

# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Reset counter daily
    now = datetime.utcnow()
    if trade_counter["date"] != now.date():
        trade_counter["count"] = 0
        trade_counter["date"] = now.date()
        trade_counter["last_reset"] = now

    # Enforce rest period after max trades
    elapsed = (now - trade_counter["last_reset"]).total_seconds() / 60
    if trade_counter["count"] >= MAX_TRADES_PER_DAY and elapsed < TRADE_RESET_MINUTES:
        await query.message.reply_text(f"⏸ Daily limit reached. Wait {int(TRADE_RESET_MINUTES - elapsed)} minutes.")
        return
    elif elapsed >= TRADE_RESET_MINUTES:
        trade_counter["count"] = 0
        trade_counter["last_reset"] = now

    if query.data == "get_signal":
        best_signal = None

        for symbol in CURRENCY_PAIRS:
            sig = generate_signal(symbol)
            if sig and sig.direction in ["BUY", "SELL"]:
                if not best_signal or sig.confidence > best_signal.confidence:
                    best_signal = sig

        if not best_signal:
            await query.message.reply_text("❌ No strong signal available right now.")
            return

        trade_counter["count"] += 1
        await send_signal(query, context, best_signal)

# =========================
# SEND SIGNAL
# =========================
async def send_signal(query, context, sig):
    caption = (
        f"📊 {sig.direction} SIGNAL\n\n"
        f"💱 Pair: {sig.symbol}\n"
        f"🔥 Confidence: {sig.confidence}%\n"
        f"💰 Price: {sig.price}\n"
        f"📈 Trend: {sig.trend}\n"
        f"⏰ Entry: {sig.entry_time}\n"
        f"⌛ Expiry: {sig.expiry_time}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ WIN", callback_data="win"),
            InlineKeyboardButton("❌ LOSS", callback_data="loss")
        ],
        [
            InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")
        ]
    ])

    await query.message.reply_text(caption, reply_markup=keyboard)

# =========================
# RUN BOT
# =========================
def run_bot():
    app = create_app()
    print("🚀 BOT RUNNING...")
    app.run_polling()