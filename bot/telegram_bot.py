from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from .config import TELEGRAM_BOT_TOKEN
from .signal_engine import generate_signal
from datetime import datetime

CURRENCIES = [
    "EUR_USD","GBP_USD","USD_JPY","USD_CHF","AUD_USD",
    "USD_CAD","NZD_USD","EUR_GBP","GBP_JPY","USD_TRY"
]

TIMEZONES = {
    "🇵🇰 PKT": "UTC+5",
    "🇮🇳 IST": "UTC+5:30",
    "🇺🇸 EST": "UTC-5",
    "🇬🇧 GMT": "UTC+0"
}

trade_data = {"count": 0, "date": datetime.utcnow().date(), "symbol": None}

# APP
def create_app():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    return app

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💱 Select Currency", callback_data="currency")],
        [InlineKeyboardButton("⏰ Select Timezone", callback_data="tz")],
        [InlineKeyboardButton("📊 Get Signal", callback_data="signal")]
    ]

    await update.message.reply_text(
        "🚀 TRADING BOT READY\nSelect option:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# BUTTONS
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    # CURRENCY MENU
    if q.data == "currency":
        keys = [[InlineKeyboardButton(c, callback_data=f"set_{c}")] for c in CURRENCIES]
        await q.message.reply_text("Select Pair:", reply_markup=InlineKeyboardMarkup(keys))

    # SET SYMBOL
    elif q.data.startswith("set_"):
        trade_data["symbol"] = q.data.replace("set_", "")
        await q.message.reply_text(f"Selected: {trade_data['symbol']}")

    # TIMEZONE MENU
    elif q.data == "tz":
        keys = [[InlineKeyboardButton(k, callback_data=f"tz_{v}")] for k,v in TIMEZONES.items()]
        await q.message.reply_text("Select Timezone:", reply_markup=InlineKeyboardMarkup(keys))

    # SIGNAL
    elif q.data == "signal":
        symbol = trade_data["symbol"] or "EUR_USD"

        sig = generate_signal(symbol)

        if not sig:
            await q.message.reply_text("❌ No Signal")
            return

        trade_data["count"] += 1

        if trade_data["count"] > 10:
            await q.message.reply_text("⏸ Rest 30 min required")
            trade_data["count"] = 0
            return

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("WIN", callback_data="win"),
             InlineKeyboardButton("LOSS", callback_data="loss")]
        ])

        await q.message.reply_text(
            f"📊 {sig.direction} SIGNAL\n"
            f"💱 {sig.symbol}\n"
            f"💰 {sig.price}\n"
            f"📈 {sig.trend}\n"
            f"⏰ Entry: {sig.entry}\n"
            f"⌛ Expiry: {sig.expiry}",
            reply_markup=keyboard
        )

# RUN
def run_bot():
    app = create_app()
    print("BOT RUNNING...")
    app.run_polling()