from telegram import Update
from telegram.ext import ContextTypes

from handlers.menu import main_menu
from services.onu import refresh_onu_cache
from handlers.info import handle_info_selection
from utils.security import (
    is_user_allowed,
    can_refresh
)


USER_STATE = {}


async def button_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if not is_user_allowed(user_id):
        await query.message.reply_text(
            "⛔ Akses ditolak.\n"
            "Anda tidak memiliki izin menggunakan bot ini."
        )
        return

    # Tombol pilihan hasil pencarian ONU / Info Pelanggan
    if data.startswith("info_select_"):
        await handle_info_selection(update, context)
        return

    if data == "menu_cari_onu":
        USER_STATE[user_id] = "cari_onu"

        await query.message.reply_text(
            "🔍 Masukkan nama pelanggan yang ingin dicari:"
        )

    elif data == "menu_refresh_onu":
        if not can_refresh(user_id):
            await query.message.reply_text(
                "⛔ Akses refresh ditolak.\n"
                "Anda tidak memiliki izin melakukan refresh data ONU.",
                reply_markup=main_menu()
            )
            return

        await query.message.reply_text(
            "🔄 Refresh data ONU sedang berjalan...\nMohon tunggu."
        )

        summary = refresh_onu_cache()

        message = (
            "✅ REFRESH ONU SELESAI\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"📦 TOTAL SITE : {summary.get('total_site', '-')}\n"
            f"📡 TOTAL PON  : {summary.get('total_pon', '-')}\n"
            f"👥 TOTAL ONU  : {summary.get('total_onu', '-')}\n\n"
            "📡 DETAIL SITE\n"
        )

        for site_name, site_data in summary.get("sites", {}).items():
            message += (
                f"\n[{site_name}]\n"
                f"Total ONU: {site_data.get('total_onu', 0)}\n"
            )

            for port, total in site_data.get("ports", {}).items():
                message += f"┣━ {port} → {total} ONU\n"

        message += "\n━━━━━━━━━━━━━━━━━━"

        await query.message.reply_text(
            message,
            reply_markup=main_menu()
        )

    elif data == "menu_help":
        message = (
            "ℹ️ BANTUAN BOT\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Menu utama:\n"
            "🔍 Cari ONU - cari pelanggan dan tampilkan info lengkap\n\n"
            "Command manual:\n"
            "/start - tampilkan menu utama\n"
            "/onu nama - cari pelanggan\n"
            "/info nama - info lengkap pelanggan\n"
            "/myid - lihat Telegram ID\n\n"
            "Command admin:\n"
            "/refresh_onu SITE PON - refresh data ONU per port\n"
            "Contoh:\n"
            "/refresh_onu BALEN 1/1/1\n"
            "/refresh_onu MAYANGKAWIS 1/1/4\n\n"
            "Catatan:\n"
            "Refresh data hanya bisa dilakukan oleh admin."
        )

        await query.message.reply_text(
            message,
            reply_markup=main_menu()
        )

    else:
        await query.message.reply_text(
            "❌ Menu tidak dikenali.",
            reply_markup=main_menu()
        )
