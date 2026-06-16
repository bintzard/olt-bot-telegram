from telegram import Update
from telegram.ext import ContextTypes

from handlers.menu import main_menu


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = (
        "✅ OLT Monitoring Bot Aktif\n\n"
        "Bot ini digunakan untuk membantu teknisi melihat informasi pelanggan.\n\n"
        "Cara pakai:\n"
        "1. Klik 🔍 Cari ONU\n"
        "2. Masukkan nama pelanggan\n"
        "3. Pilih pelanggan dari daftar\n"
        "4. Bot akan menampilkan info lengkap:\n"
        "   - Lokasi\n"
        "   - IP PPPoE\n"
        "   - Status PPPoE\n"
        "   - ONU / PON / ID\n"
        "   - Status ONU\n"
        "   - Redaman / power\n\n"
        "Silakan pilih menu di bawah."
    )

    await update.message.reply_text(
        message,
        reply_markup=main_menu()
    )
