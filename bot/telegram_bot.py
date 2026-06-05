from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
from .config import TELEGRAM_BOT_TOKEN
from .signal_engine import generate_signal

CURRENCY_PAIRS = [
    "EUR_USD","GBP_USD","USD_JPY","USD_CHF","AUD_USD",
    "USD_CAD","NZD_USD","EUR_GBP","GBP_JPY","USD_TRY"
]

MAX_TRADES_PER_DAY = 10

trade_counter = {
    "count": 0,
    "date": datetime.utcnow().date()
}

# ================= APP =================
def create_app():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    return app


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trade_counter["count"] = 0
    trade_counter["date"] = datetime.utcnow().date()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])

    await update.message.reply_text(
        "🚀 TRADING BOT READY\n\n"
        "📊 Click below to get signal",
        reply_markup=keyboard
    )


# ================= BUTTON =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # reset daily
    if trade_counter["date"] != datetime.utcnow().date():
        trade_counter["count"] = 0
        trade_counter["date"] = datetime.utcnow().date()

    # limit check
    if trade_counter["count"] >= MAX_TRADES_PER_DAY:
        await query.message.reply_text("⚠️ Daily limit reached (10 trades)")
        return

    if query.data == "get_signal":
        best = None

        for symbol in CURRENCY_PAIRS:
            sig = generate_signal(symbol)
            if sig and sig.direction in ["BUY", "SELL"]:
                if not best or sig.confidence > best.confidence:
                    best = sig

        if not best:
            await query.message.reply_text("❌ No signal found")
            return

        trade_counter["count"] += 1
        await send_signal(query, context, best)


# ================= SEND =================
async def send_signal(query, context, sig):
    caption = (
        f"📊 {sig.direction} SIGNAL\n"
        f"💱 {sig.symbol}\n"
        f"🔥 {sig.confidence}%\n"
        f"💰 {sig.price}\n"
        f"📈 {sig.trend}\n"
        f"⏰ Entry: {sig.entry_time}\n"
        f"⌛ Expiry: {sig.expiry_time}"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("WIN", callback_data="win"),
            InlineKeyboardButton("LOSS", callback_data="loss")
        ],
        [
            InlineKeyboardButton("GET SIGNAL", callback_data="get_signal")
        ]
    ])

    await query.message.reply_text(caption, reply_markup=keyboard)


# ================= RUN =================
def run_bot():
    app = create_app()
    print("BOT RUNNING...")
    app.run_polling()