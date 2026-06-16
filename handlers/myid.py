from telegram import Update
from telegram.ext import ContextTypes


async def my_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    username = update.effective_user.username
    name = update.effective_user.full_name

    message = (
        "🆔 TELEGRAM USER INFO\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"NAME : {name}\n"
        f"USER : @{username}\n"
        f"ID   : {user_id}\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(message)
