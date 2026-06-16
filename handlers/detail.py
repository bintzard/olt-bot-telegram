from telegram import Update
from telegram.ext import ContextTypes

from services.onu_cache import search_onu_cache
from services.ssh_client import SSHClient
from parser.detail_parser import parse_onu_detail
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


def format_status(phase_state):
    phase = phase_state.lower()

    if phase == "working":
        return "🟢 ONLINE"

    if phase == "offline":
        return "🔴 OFFLINE"

    return f"🟡 {phase_state}"


async def detail_onu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await deny_access(update)
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/detail nama_pelanggan\n\nContoh:\n/detail sucipto"
        )
        return

    keyword = " ".join(context.args)

    result = search_onu_cache(keyword)

    if not result:
        await update.message.reply_text(
            f"❌ ONU '{keyword}' tidak ditemukan.",
            reply_markup=main_menu()
        )
        return

    onu_cache = result[0]
    interface = onu_cache["interface"]

    await update.message.reply_text(
        f"🔍 Mengambil detail ONU:\n{interface}"
    )

    command = f"show gpon onu detail-info {interface}"
    output = ssh.execute(command, wait_time=8)

    if not output or output.startswith("ERROR"):
        await update.message.reply_text(
            "❌ Gagal mengambil detail ONU.",
            reply_markup=main_menu()
        )
        return

    detail = parse_onu_detail(output)

    name = clean_name(detail["name"])
    description = clean_description(detail["description"])
    status = format_status(detail["phase_state"])

    message = (
        "📡 DETAIL ONU\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"NAME   : {name}\n"
        f"ONU    : {detail['interface']}\n"
        f"TYPE   : {detail['type']}\n"
        f"SN     : {detail['serial_number']}\n"
        f"DESC   : {description}\n\n"
        f"STATUS : {status}\n"
        f"STATE  : {detail['state']}\n"
        f"ADMIN  : {detail['admin_state']}\n"
        f"CONFIG : {detail['config_state']}\n"
        f"UPTIME : {detail['online_duration']}\n"
        f"DIST   : {detail['onu_distance']}\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(
        message,
        reply_markup=main_menu()
    )
