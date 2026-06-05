from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from .signal_engine import generate_signal
from .config import TELEGRAM_BOT_TOKEN
from datetime import datetime
import time

# =========================
# PAIRS
# =========================
CURRENCY_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "USD_CHF", "AUD_USD",
    "USD_CAD", "NZD_USD", "EUR_GBP", "GBP_JPY", "USD_TRY"
]

# =========================
# USER STATE (10 trades + cooldown)
# =========================
user_state = {}
MAX_TRADES = 10
COOLDOWN_SECONDS = 30 * 60

# =========================
# APP
# =========================
def create_app():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    return app

# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    user_state[user_id] = {
        "count": 0,
        "cooldown": 0,
        "pair": "EUR_USD",
        "timezone": "UTC"
    }

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💱 Select Pair", callback_data="pair")],
        [InlineKeyboardButton("🌍 Select Timezone", callback_data="tz")],
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])

    await update.message.reply_text(
        "👋 Trading Bot Ready\n\n"
        "📌 Rules:\n"
        "• 10 Trades per session\n"
        "• 30 min cooldown after limit\n"
        "• Select your pair & timezone\n\n"
        "👇 Start below",
        reply_markup=keyboard
    )

# =========================
# HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in user_state:
        user_state[user_id] = {"count": 0, "cooldown": 0, "pair": "EUR_USD"}

    state = user_state[user_id]

    # cooldown check
    if time.time() < state["cooldown"]:
        await query.message.reply_text("⏳ 30 min cooldown active. Try later.")
        return

    # GET SIGNAL
    if query.data == "get_signal":

        if state["count"] >= MAX_TRADES:
            state["cooldown"] = time.time() + COOLDOWN_SECONDS
            state["count"] = 0
            await query.message.reply_text("⚠️ 10 trades done. 30 min cooldown started.")
            return

        symbol = state["pair"]
        sig = generate_signal(symbol)

        if not sig or sig.direction not in ["BUY", "SELL"]:
            await query.message.reply_text("❌ No strong signal")
            return

        state["count"] += 1
        await send_signal(query, context, sig)

# =========================
# SEND SIGNAL
# =========================
async def send_signal(query, context, sig):

    image_path = "assets/buy.png" if sig.direction == "BUY" else "assets/sell.png"

    caption = (
        f"● {sig.direction} SIGNAL\n\n"
        f"{sig.symbol}\n"
        f"🔥 {sig.confidence}%\n\n"
        f"Entry: {sig.entry_time}\n"
        f"Expiry: {sig.expiry_time}\n\n"
        "⚡ Hurry — 25s left"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ WIN", callback_data="win"),
            InlineKeyboardButton("❌ LOSS", callback_data="loss")
        ],
        [InlineKeyboardButton("📊 GET SIGNAL", callback_data="get_signal")]
    ])

    try:
        with open(image_path, "rb") as img:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=img,
                caption=caption,
                reply_markup=keyboard
            )
    except Exception as e:
        await query.message.reply_text(f"ERROR: {e}")

# =========================
# RUN
# =========================
def run_bot():
    app = create_app()
    print("🚀 Bot running...")
    app.run_polling()