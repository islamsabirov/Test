import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from database import init_db
from utils import check_subscription

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await check_subscription(update):
        return
    await update.message.reply_text(
        f"Xush kelibsiz, {user.first_name}! Kino kodi yoki nomini yuboring."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update):
        return
    text = update.message.text
    await update.message.reply_text(
        f"Kino qidirilmoqda: {text}\n(Hozir demo bot)"
    )


async def main():
    await init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
