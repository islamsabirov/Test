"""
╔══════════════════════════════════════════════════════╗
║   🎬 KinoBot — Python Telegram Bot                  ║
║   ✅ Polling rejimi — hamma serverda ishlaydi        ║
╚══════════════════════════════════════════════════════╝
"""

import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ChatMemberHandler,
    ChatJoinRequestHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram.error import (
    TelegramError,
    Forbidden,
    NetworkError,
    BadRequest,
    TimedOut,
)

# ── .env yuklash ──────────────────────────────────────────────
load_dotenv()

# ✅ TO'G'RI — getenv ga NOMI beriladi, qiymat emas
BOT_TOKEN : str = os.getenv("BOT_TOKEN", "")
OWNER_ID  : int = int(os.getenv("OWNER_ID", "0"))

# ── Import ────────────────────────────────────────────────────
from db import db
from handlers.cmd    import cmd_start, cmd_help, cmd_panel
from handlers.msg    import msg_router
from handlers.cb     import cb_router
from handlers.member import on_my_chat_member, on_chat_join_request

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d.%m.%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
log = logging.getLogger("KinoBot")


# ── Error handler ─────────────────────────────────────────────
async def error_handler(update: object, ctx) -> None:
    err = ctx.error
    # Foydalanuvchi botni bloklagan
    if isinstance(err, Forbidden):
        if update and hasattr(update, "effective_user") and update.effective_user:
            db.user_mark_left(update.effective_user.id)
        return
    # Internet muammosi — o'zi qayta urinadi
    if isinstance(err, (NetworkError, TimedOut)):
        log.warning(f"Tarmoq xatosi: {err}")
        return
    # Noto'g'ri so'rov
    if isinstance(err, BadRequest):
        log.warning(f"BadRequest: {err}")
        return
    # Boshqa xatolar
    log.error("Xato:", exc_info=ctx.error)


# ── Startup ───────────────────────────────────────────────────
async def on_startup(app: Application) -> None:
    me = await app.bot.get_me()
    log.info(f"✅ Bot ishga tushdi: @{me.username} (ID: {me.id})")
    log.info(f"👑 Owner ID: {OWNER_ID}")
    try:
        await app.bot.send_message(
            OWNER_ID,
            f"🟢 <b>Bot ishga tushdi!</b>\n\n"
            f"🤖 @{me.username}\n"
            f"👥 Foydalanuvchilar: {db.user_count()} ta\n"
            f"🎬 Kinolar: {db.movie_count()} ta",
            parse_mode="HTML",
        )
    except TelegramError:
        pass


# ── Main ──────────────────────────────────────────────────────
def main() -> None:
    if not BOT_TOKEN:
        log.critical("❌ BOT_TOKEN topilmadi! .env faylini to'ldiring.")
        sys.exit(1)
    if not OWNER_ID:
        log.critical("❌ OWNER_ID topilmadi! .env faylini to'ldiring.")
        sys.exit(1)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start",  cmd_start))
    app.add_handler(CommandHandler("help",   cmd_help))
    app.add_handler(CommandHandler("panel",  cmd_panel))
    app.add_handler(CommandHandler("admin",  cmd_panel))
    app.add_handler(CommandHandler("a",      cmd_panel))
    app.add_handler(CommandHandler("p",      cmd_panel))

    # Callbacks
    app.add_handler(CallbackQueryHandler(cb_router))

    # Chat member / join request
    app.add_handler(ChatMemberHandler(on_my_chat_member,
                                      ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(ChatJoinRequestHandler(on_chat_join_request))

    # Messages (faqat private chat)
    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & ~filters.COMMAND,
        msg_router,
    ))

    # ✅ Error handler — bu bo'lmasa konsol xato chiqaradi
    app.add_error_handler(error_handler)

    log.info("🔄 Polling boshlandi...")
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
