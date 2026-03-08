"""
╔══════════════════════════════════════════════════════╗
║   🎬 KinoBot — Python Telegram Bot                  ║
║   ✅ Polling rejimi — hamma serverda ishlaydi        ║
║   ✅ Render / VPS / Shared / Lokal                   ║
║   ✅ python-telegram-bot 20+                         ║
╚══════════════════════════════════════════════════════╝
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    InlineQueryHandler,
    filters,
)
from telegram.error import TelegramError

# ──────────────────────────────────────────────────────────────
#  ⚙️  CONFIG & LOGGING
# ──────────────────────────────────────────────────────────────
BOT_TOKEN = "BOT_TOKEN"
OWNER_ID = 5907118746  # Admin ID
from database import db
from handlers import (
    start_handler,
    help_handler,
    message_handler,
    callback_handler,
    inline_query_handler,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Bot ishga tushganda bajariladi"""
    db.init_dirs()
    me = await application.bot.get_me()
    logger.info(f"✅ Bot ishga tushdi: @{me.username} (ID: {me.id})")
    logger.info(f"👑 Owner ID: {OWNER_ID}")
    try:
        await application.bot.send_message(
            chat_id=OWNER_ID,
            text=(
                "🟢 <b>Bot ishga tushdi!</b>\n\n"
                f"🤖 Bot: @{me.username}\n"
                f"🆔 ID: <code>{me.id}</code>\n"
                "📡 Rejim: Polling"
            ),
            parse_mode="HTML",
        )
    except TelegramError:
        pass


def main() -> None:
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN topilmadi! .env yoki environment variables ga qo'shing.")
        sys.exit(1)
    if not OWNER_ID:
        logger.error("❌ OWNER_ID topilmadi! .env yoki environment variables ga qo'shing.")
        sys.exit(1)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Handlers
    app.add_handler(CommandHandler("start",   start_handler))
    app.add_handler(CommandHandler("help",    help_handler))
    app.add_handler(CommandHandler("panel",   start_handler))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    app.add_handler(InlineQueryHandler(inline_query_handler))

    logger.info("🔄 Polling boshlandi...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
