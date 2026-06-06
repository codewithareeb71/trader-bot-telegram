from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime

from bot.config import TELEGRAM_BOT_TOKEN
from bot.signal_engine import generate_signal

CURRENCY_PAIRS = [
    "EUR_USD","GBP_USD","USD_JPY","USD_CHF","AUD_USD",
    "USD_CAD","NZD_USD","EUR_GBP","GBP_JPY","USD_TRY"
]

MAX_TRADES_PER_DAY = 10

trade_counter = {
    "count": 0,
    "date": datetime.utcnow().date()
}

def create_app():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    return app

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trade_counter["count"] = 0
    trade_counter["date"] = datetime.utcnow().date()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])

    await update.message.reply_text(
        "🚀 TRADING BOT READY\n⚡ Click button to get signal",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    now = datetime.utcnow()

    if trade_counter["date"] != now.date():
        trade_counter["count"] = 0
        trade_counter["date"] = now.date()

    if trade_counter["count"] >= MAX_TRADES_PER_DAY:
        await query.message.reply_text("⚠️ Daily limit reached")
        return

    if query.data == "get_signal":

        best = None

        for symbol in CURRENCY_PAIRS:
            sig = generate_signal(symbol)
            if sig and sig.direction in ["BUY", "SELL"]:
                if not best or sig.confidence > best.confidence:
                    best = sig

        if not best:
            await query.message.reply_text("❌ No signal")
            return

        trade_counter["count"] += 1

        text = (
            f"📊 {best.direction} SIGNAL\n"
            f"💱 {best.symbol}\n"
            f"🔥 {best.confidence}%\n"
            f"💰 {best.price}\n"
            f"📈 {best.trend}\n"
            f"⏰ {best.entry}\n"
            f"⌛ {best.expiry}"
        )

        await query.message.reply_text(text)

def run_bot():
    app = create_app()
    print("🚀 BOT RUNNING...")
    app.run_polling()