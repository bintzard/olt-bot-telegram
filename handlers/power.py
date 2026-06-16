from telegram import Update
from telegram.ext import ContextTypes

from services.onu_cache import search_onu_cache
from services.ssh_client import SSHClient
from parser.power_parser import parse_power_output
from handlers.menu import main_menu
from utils.security import is_user_allowed, deny_access


from dotenv import load_dotenv
import os


load_dotenv()


OLT_HOST = os.getenv("OLT_HOST")
OLT_USER = os.getenv("OLT_USER")
OLT_PASS = os.getenv("OLT_PASS")


ssh = SSHClient(
    host=OLT_HOST,
    username=OLT_USER,
    password=OLT_PASS
)


def clean_name(name):
    return name.lstrip("0123456789")


def clean_description(description):
    return (
        description
        .replace("$", "")
        .replace("_", " ")
    )


def power_quality(onu_rx):
    try:
        rx = float(onu_rx)
    except:
        return "⚪ UNKNOWN"

    if rx >= -24:
        return "🟢 BAGUS"

    if rx >= -27:
        return "🟡 SEDANG"

    return "🔴 BURUK"


async def power_onu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await deny_access(update)
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/power nama_pelanggan\n\nContoh:\n/power sucipto"
        )
        return

    keyword = " ".join(context.args)

    result = search_onu_cache(keyword)

    if not result:
        await update.message.reply_text(
            f"❌ ONU '{keyword}' tidak ditemukan."
        )
        return

    onu = result[0]
    interface = onu["interface"]

    await update.message.reply_text(
        f"📶 Mengambil redaman ONU:\n{interface}"
    )

    command = f"show pon power attenuation {interface}"
    output = ssh.execute(command, wait_time=8)

    if not output or output.startswith("ERROR"):
        await update.message.reply_text(
            "❌ Gagal mengambil data redaman ONU."
        )
        return

    power = parse_power_output(output)

    name = clean_name(onu.get("name", "-"))
    description = clean_description(onu.get("description", "-"))
    quality = power_quality(power["onu_rx"])

    message = (
        "📶 POWER / REDAMAN ONU\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"NAME : {name}\n"
        f"ONU  : {interface}\n"
        f"PON  : {onu.get('pon', '-')}\n"
        f"ID   : {onu.get('onu_id', '-')}\n"
        f"DESC : {description}\n\n"

        f"QUALITY : {quality}\n\n"

        "📤 UPSTREAM (ONU → OLT)\n"
        f"OLT RX : {power['olt_rx']} dBm\n"
        f"ONU TX : {power['onu_tx']} dBm\n"
        f"LOSS   : {power['up_attenuation']} dB\n\n"

        "📥 DOWNSTREAM (OLT → ONU)\n"
        f"OLT TX : {power['olt_tx']} dBm\n"
        f"ONU RX : {power['onu_rx']} dBm\n"
        f"LOSS   : {power['down_attenuation']} dB\n"

        "━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(
        message,
        reply_markup=main_menu()
    )
