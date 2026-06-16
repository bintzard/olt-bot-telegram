from telegram import Update
from telegram.ext import ContextTypes

from services.onu import refresh_onu_cache
from handlers.menu import main_menu
from utils.security import (
    is_user_allowed,
    deny_access,
    can_refresh
)
from config.device import DEVICES


async def refresh_onu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await deny_access(update)
        return

    if not can_refresh(user_id):
        await update.message.reply_text(
            "⛔ Akses refresh ditolak.\n"
            "Anda tidak memiliki izin melakukan refresh data ONU.",
            reply_markup=main_menu()
        )
        return

    if len(context.args) == 0:
        sites = ", ".join(DEVICES.keys())

        await update.message.reply_text(
            "Usage:\n"
            "/refresh_onu SITE\n"
            "/refresh_onu SITE PON\n\n"
            "Contoh:\n"
            "/refresh_onu BALEN\n"
            "/refresh_onu BALEN 1/1/1\n\n"
            f"SITE tersedia:\n{sites}",
            reply_markup=main_menu()
        )
        return

    site = context.args[0].upper()
    target_port = context.args[1] if len(context.args) > 1 else None

    if site not in DEVICES:
        sites = ", ".join(DEVICES.keys())

        await update.message.reply_text(
            f"❌ Site '{site}' tidak ditemukan.\n\n"
            f"SITE tersedia:\n{sites}",
            reply_markup=main_menu()
        )
        return

    if target_port:
        await update.message.reply_text(
            f"🔄 Refresh ONU site {site} port {target_port} sedang berjalan...\nMohon tunggu."
        )
    else:
        await update.message.reply_text(
            f"🔄 Refresh semua port site {site} sedang berjalan...\nMohon tunggu."
        )

    try:
        summary = refresh_onu_cache(
            site,
            target_port
        )

        message = (
            "✅ REFRESH ONU SELESAI\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"SITE REFRESH : {site}\n"
            f"📦 TOTAL SITE : {summary['total_site']}\n"
            f"📡 TOTAL PON  : {summary['total_pon']}\n"
            f"👥 TOTAL ONU  : {summary['total_onu']}\n\n"
            "📡 DETAIL SITE\n"
        )

        for site_name, site_data in summary["sites"].items():
            message += (
                f"\n[{site_name}]\n"
                f"Total ONU: {site_data['total_onu']}\n"
            )

            for port, total in site_data["ports"].items():
                message += f"┣━ {port} → {total} ONU\n"

        message += "\n━━━━━━━━━━━━━━━━━━"

        await update.message.reply_text(
            message,
            reply_markup=main_menu()
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ Refresh ONU gagal:\n{str(e)}",
            reply_markup=main_menu()
        )
