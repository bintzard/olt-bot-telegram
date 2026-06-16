from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.onu import check_onu
from handlers.menu import main_menu
from handlers.info import INFO_SELECTIONS
from utils.security import is_user_allowed, deny_access


def format_name(name):
    return name.lstrip("0123456789")


def format_description(description):
    return (
        description
        .replace("$", "")
        .replace("_", " ")
    )


def build_onu_result_keyboard(results):
    keyboard = []

    for index, onu in enumerate(results[:10]):
        name = format_name(
            onu.get("name", "-")
        )

        site = onu.get("site", "-")
        pon = onu.get("pon", "-")
        onu_id = onu.get("onu_id", "-")
        description = format_description(
            onu.get("description", "-")
        )

        button_text = (
            f"👤 {name} | {site} | {pon}:{onu_id}"
        )

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"info_select_{index}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🏠 Menu Utama",
            callback_data="menu_help"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


async def onu_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await deny_access(update)
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/onu nama_pelanggan\n\nContoh:\n/onu sucipto"
        )
        return

    keyword = " ".join(context.args)

    await update.message.reply_text(
        f"🔎 Mencari ONU dengan nama:\n{keyword}"
    )

    result = check_onu(keyword)

    if not result:
        await update.message.reply_text(
            f"❌ ONU dengan nama '{keyword}' tidak ditemukan.",
            reply_markup=main_menu()
        )
        return

    total_result = len(result)
    result = result[:10]

    INFO_SELECTIONS[user_id] = {
        "keyword": keyword,
        "results": result
    }

    message = (
        "🔎 HASIL PENCARIAN ONU\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Kata kunci : {keyword}\n"
        f"Ditemukan  : {total_result} data\n"
        f"Ditampilkan: {len(result)} data\n\n"
        "Silakan pilih pelanggan di tombol bawah."
    )

    if total_result > 10:
        message += (
            "\n\n⚠️ Hasil terlalu banyak.\n"
            "Ditampilkan 10 data pertama saja.\n"
            "Gunakan nama yang lebih spesifik jika data belum muncul."
        )

    await update.message.reply_text(
        message,
        reply_markup=build_onu_result_keyboard(result)
    )
