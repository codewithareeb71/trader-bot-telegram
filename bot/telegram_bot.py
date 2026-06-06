from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime, timedelta

from bot.config import TELEGRAM_BOT_TOKEN
from bot.signal_engine import generate_signal

# ===== CONFIG =====
CURRENCY_PAIRS = [
    "EUR_USD","GBP_USD","USD_JPY","USD_CHF","AUD_USD",
    "USD_CAD","NZD_USD","EUR_GBP","GBP_JPY","USD_TRY"
]

TIMEZONES = {
    "🇵🇰 PKT": "UTC+5",
    "🇮🇳 IST": "UTC+5:30",
    "🇺🇸 EST": "UTC-5",
    "🇬🇧 GMT": "UTC+0"
}

MAX_TRADES_PER_DAY = 10
TRADE_RESET_MINUTES = 30

trade_counter = {
    "count": 0,
    "date": datetime.utcnow().date(),
    "last_reset": datetime.utcnow(),
    "symbol": None,
    "timezone": "UTC+0"
}

# ===== APP SETUP =====
def create_app():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    return app

# ===== START COMMAND =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trade_counter["count"] = 0
    trade_counter["date"] = datetime.utcnow().date()
    trade_counter["last_reset"] = datetime.utcnow()

    keyboard = [
        [InlineKeyboardButton("💱 Select Currency", callback_data="currency")],
        [InlineKeyboardButton("⏰ Select Timezone", callback_data="timezone")],
        [InlineKeyboardButton("📊 Get Signal", callback_data="get_signal")]
    ]
    await update.message.reply_text(
        "🚀 TRADER BOT READY\nSelect option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===== BUTTON HANDLER =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    now = datetime.utcnow()
    # Daily reset
    if trade_counter["date"] != now.date():
        trade_counter["count"] = 0
        trade_counter["date"] = now.date()
        trade_counter["last_reset"] = now

    # Rest period after max trades
    elapsed = (now - trade_counter["last_reset"]).total_seconds() / 60
    if trade_counter["count"] >= MAX_TRADES_PER_DAY and elapsed < TRADE_RESET_MINUTES:
        await query.message.reply_text(f"⏸ Daily limit reached. Wait {int(TRADE_RESET_MINUTES - elapsed)} min.")
        return
    elif elapsed >= TRADE_RESET_MINUTES:
        trade_counter["count"] = 0
        trade_counter["last_reset"] = now

    # ===== CURRENCY SELECT =====
    if query.data == "currency":
        keys = [[InlineKeyboardButton(c, callback_data=f"set_{c}")] for c in CURRENCY_PAIRS]
        await query.message.reply_text("Select Currency:", reply_markup=InlineKeyboardMarkup(keys))
        return

    if query.data.startswith("set_"):
        trade_counter["symbol"] = query.data.replace("set_", "")
        await query.message.reply_text(f"✅ Selected Currency: {trade_counter['symbol']}")
        return

    # ===== TIMEZONE SELECT =====
    if query.data == "timezone":
        keys = [[InlineKeyboardButton(k, callback_data=f"tz_{v}")] for k, v in TIMEZONES.items()]
        await query.message.reply_text("Select Timezone:", reply_markup=InlineKeyboardMarkup(keys))
        return

    if query.data.startswith("tz_"):
        trade_counter["timezone"] = query.data.replace("tz_", "")
        await query.message.reply_text(f"🕒 Timezone set: {trade_counter['timezone']}")
        return

    # ===== GET SIGNAL =====
    if query.data == "get_signal":
        symbol = trade_counter["symbol"] or "EUR_USD"
        best_signal = generate_signal(symbol)

        if not best_signal:
            await query.message.reply_text("❌ No strong signal right now.")
            return

        trade_counter["count"] += 1

        caption = (
            f"📊 {best_signal.direction} SIGNAL\n"
            f"💱 Pair: {best_signal.symbol}\n"
            f"🔥 Confidence: {best_signal.confidence}%\n"
            f"💰 Price: {best_signal.price}\n"
            f"📈 Trend: {best_signal.trend}\n"
            f"⏰ Entry: {best_signal.entry}\n"
            f"⌛ Expiry: {best_signal.expiry}\n"
            f"🕒 Timezone: {trade_counter['timezone']}"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ WIN", callback_data="win"),
             InlineKeyboardButton("❌ LOSS", callback_data="loss")],
            [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
        ])

        await query.message.reply_text(caption, reply_markup=keyboard)

# ===== RUN BOT =====
def run_bot():
    app = create_app()
    print("🚀 BOT RUNNING...")
    app.run_polling()