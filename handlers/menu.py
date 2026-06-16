from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "🔍 Cari ONU",
                callback_data="menu_cari_onu"
            )
        ],
        [
            InlineKeyboardButton(
                "ℹ️ Bantuan",
                callback_data="menu_help"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)
