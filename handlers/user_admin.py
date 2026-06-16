from telegram import Update
from telegram.ext import ContextTypes

from utils.security import (
    load_security_data,
    save_security_data,
    is_owner,
    deny_access
)


async def add_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not is_owner(user_id):
        await deny_access(update)
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/adduser telegram_id"
        )
        return

    try:
        new_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Telegram ID harus berupa angka."
        )
        return

    data = load_security_data()
    allowed_users = data.get("allowed_users", [])

    if new_user_id not in allowed_users:
        allowed_users.append(new_user_id)

    data["allowed_users"] = allowed_users
    save_security_data(data)

    await update.message.reply_text(
        f"✅ User {new_user_id} berhasil ditambahkan."
    )


async def remove_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not is_owner(user_id):
        await deny_access(update)
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/removeuser telegram_id"
        )
        return

    try:
        target_user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Telegram ID harus berupa angka."
        )
        return

    data = load_security_data()
    allowed_users = data.get("allowed_users", [])

    if target_user_id in allowed_users:
        allowed_users.remove(target_user_id)

    data["allowed_users"] = allowed_users
    save_security_data(data)

    await update.message.reply_text(
        f"✅ User {target_user_id} berhasil dihapus."
    )


async def list_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not is_owner(user_id):
        await deny_access(update)
        return

    data = load_security_data()

    message = (
        "👥 DAFTAR USER BOT\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"OWNER ID:\n{data.get('owner_id')}\n\n"
        "ALLOWED USERS:\n"
    )

    for allowed_user in data.get("allowed_users", []):
        message += f"- {allowed_user}\n"

    message += "━━━━━━━━━━━━━━━━━━"

    await update.message.reply_text(message)
