import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from database import get_active_channels

logger = logging.getLogger(__name__)

def check_subscription(update, context):
    """Foydalanuvchining barcha kanallarga obunasini tekshiradi"""
    user_id = update.effective_user.id
    bot = context.bot
    
    # Majburiy kanallarni olish
    channels = get_active_channels()
    
    if not channels:
        return True
    
    # Har bir kanalni tekshirish
    not_subscribed_channels = []
    
    for channel in channels:
        try:
            member = bot.get_chat_member(chat_id=channel.chat_id, user_id=user_id)
            if member.status in ['left', 'kicked']:
                not_subscribed_channels.append(channel)
        except Exception as e:
            logger.error(f"Kanal tekshirishda xatolik: {e}")
            not_subscribed_channels.append(channel)
    
    if not_subscribed_channels:
        send_subscription_message(update, context, not_subscribed_channels)
        return False
    
    return True

def send_subscription_message(update, context, channels):
    """Obuna bo'lmagan kanallar uchun xabar yuboradi"""
    keyboard = []
    
    for channel in channels:
        keyboard.append([InlineKeyboardButton(
            text=f"📢 {channel.name}", 
            url=channel.invite_link
        )])
    
    keyboard.append([InlineKeyboardButton(
        text="✅ Obuna bo'ldim", 
        callback_data="check_subscription"
    )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        "⚠️ Botdan foydalanish uchun quyidagi kanal(lar)ga obuna bo'ling:\n\n"
        "Quyidagi kanallarga a'zo bo'ling va '✅ Obuna bo'ldim' tugmasini bosing."
    )
    
    update.message.reply_text(
        text=text,
        reply_markup=reply_markup
    )
