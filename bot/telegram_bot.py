from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from .signal_engine import generate_signal
from .config import TELEGRAM_BOT_TOKEN
from datetime import datetime

CURRENCY_PAIRS = ["EUR_USD","GBP_USD","USD_JPY","USD_CHF","AUD_USD",
                  "USD_CAD","NZD_USD","EUR_GBP","GBP_JPY","USD_TRY"]

MAX_TRADES_PER_DAY = 10  # new rule
trade_counter = {"count": 0, "date": datetime.utcnow().date()}

def create_app():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    return app

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trade_counter["count"] = 0
    trade_counter["date"] = datetime.utcnow().date()

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]])
    await update.message.reply_text(
        f"👋 Trading Bot Ready\n📌 Max Trades/Day: {MAX_TRADES_PER_DAY}\n👇 Click to start",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Reset daily
    if trade_counter["date"] != datetime.utcnow().date():
        trade_counter["count"] = 0
        trade_counter["date"] = datetime.utcnow().date()

    if trade_counter["count"] >= MAX_TRADES_PER_DAY:
        await query.message.reply_text(f"⚠️ Daily limit reached ({MAX_TRADES_PER_DAY} trades)")
        return

    if query.data == "get_signal":
        best_signal = None
        for symbol in CURRENCY_PAIRS:
            sig = generate_signal(symbol)
            if sig and sig.direction in ["BUY","SELL"]:
                if not best_signal or sig.confidence > best_signal.confidence:
                    best_signal = sig
        if not best_signal:
            await query.message.reply_text("❌ No strong signal")
            return

        trade_counter["count"] += 1
        await send_signal(query, context, best_signal)

async def send_signal(query, context, sig):
    image_path = "assets/buy.png" if sig.direction=="BUY" else "assets/sell.png"
    caption = f"📊 {sig.direction} SIGNAL\n💱 {sig.symbol}\n🔥 {sig.confidence}%\n💰 {sig.price}\n⏰ Entry: {sig.entry_time}\n⌛ Expiry: {sig.expiry_time}\n📡 Trend: {sig.trend}"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ WIN", callback_data="win"),
         InlineKeyboardButton("❌ LOSS", callback_data="loss")],
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])
    try:
        with open(image_path,"rb") as img:
            await context.bot.send_photo(chat_id=query.message.chat_id,
                                         photo=img,
                                         caption=caption,
                                         reply_markup=keyboard)
    except Exception as e:
        await query.message.reply_text(f"⚠️ IMAGE ERROR: {str(e)}")

def run_bot():
    app = create_app()
    print("🚀 Bot running...")
    app.run_polling()