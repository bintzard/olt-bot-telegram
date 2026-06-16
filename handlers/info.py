from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from services.onu_cache import search_onu_cache
from services.ssh_client import SSHClient
from services.mikrotik import get_pppoe_info
from parser.detail_parser import parse_onu_detail
from parser.power_parser import parse_power_output
from handlers.menu import main_menu
from utils.security import is_user_allowed, deny_access
from config.device import DEVICES


INFO_SELECTIONS = {}


def clean_name(name):
    return name.lstrip("0123456789")


def clean_description(description):
    return (
        description
        .replace("$", "")
        .replace("_", " ")
    )


def normalize_lookup(text):
    return (
        text.lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .strip()
    )


def customer_match_key(name):
    name = name.lower().strip()
    name = name.lstrip("0123456789")

    if "_" in name:
        name = name.split("_")[0]

    return normalize_lookup(name)


def select_exact_onu(keyword, onu_results):
    keyword_key = normalize_lookup(keyword)

    exact_results = []

    for onu in onu_results:
        name = onu.get("name", "-")
        match_key = customer_match_key(name)

        if match_key == keyword_key:
            exact_results.append(onu)

    if len(exact_results) == 1:
        return exact_results[0], None

    if len(exact_results) > 1:
        return None, exact_results

    return None, onu_results


def build_selection_keyboard(results):
    keyboard = []

    for index, onu in enumerate(results[:10]):
        name = clean_name(
            onu.get("name", "-")
        )

        site = onu.get("site", "-")
        pon = onu.get("pon", "-")
        onu_id = onu.get("onu_id", "-")

        button_text = (
            f"{index + 1}. {name} | {site} | {pon}:{onu_id}"
        )

        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"info_select_{index}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "❌ Batal",
            callback_data="info_select_cancel"
        )
    ])

    return InlineKeyboardMarkup(keyboard)


def format_multiple_onu_message(keyword, results):
    message = (
        "⚠️ DITEMUKAN DATA MIRIP\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"Kata kunci : {keyword}\n\n"
    )

    limited_results = results[:10]

    for index, onu in enumerate(limited_results, start=1):
        name = clean_name(
            onu.get("name", "-")
        )

        description = clean_description(
            onu.get("description", "-")
        )

        message += (
            f"{index}. {name}\n"
            f"   LOKASI : {onu.get('site', '-')}\n"
            f"   ONU    : {onu.get('interface', '-')}\n"
            f"   DESC   : {description}\n\n"
        )

    if len(results) > 10:
        message += (
            f"Ditampilkan 10 dari {len(results)} data.\n"
            "Gunakan nama yang lebih spesifik jika belum muncul.\n\n"
        )

    message += (
        "Silakan pilih data pelanggan yang sesuai.\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    return message


def pppoe_candidates(name):
    name = name.lower().strip()

    clean_number = name.lstrip("0123456789")
    clean_zero = name.lstrip("0")

    base_name = clean_number.split("_")[0]

    candidates = [
        name,
        clean_zero,
        clean_number,
        base_name
    ]

    return list(dict.fromkeys(candidates))


def format_status(phase_state):
    phase = phase_state.lower()

    if phase == "working":
        return "🟢 ONLINE"

    if phase == "offline":
        return "🔴 OFFLINE"

    return f"🟡 {phase_state}"


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


def get_olt_ssh(site):
    site = site.upper()

    device = DEVICES.get(site)

    if not device:
        raise ValueError(
            f"Lokasi '{site}' tidak ditemukan di config/device.py"
        )

    olt = device["olt"]

    return SSHClient(
        host=olt["host"],
        username=olt["username"],
        password=olt["password"]
    )


async def send_customer_info(message_obj, keyword, onu):
    site = onu.get("site", "BALEN").upper()
    interface = onu["interface"]

    ssh = get_olt_ssh(site)

    await message_obj.reply_text(
        f"🔍 Mengambil info pelanggan:\n{keyword}\n\nLOKASI: {site}"
    )

    detail_output = ssh.execute(
        f"show gpon onu detail-info {interface}",
        wait_time=8
    )

    power_output = ssh.execute(
        f"show pon power attenuation {interface}",
        wait_time=8
    )

    detail = parse_onu_detail(detail_output)
    power = parse_power_output(power_output)

    pppoe_data = None

    pon = onu.get("pon", "-")
    onu_id = onu.get("onu_id", "-")

    # Prioritas 1: cari berdasarkan PON:ID
    # Contoh: 1/2/6:63
    if pon != "-" and onu_id != "-":
        pppoe_key = f"{pon}:{onu_id}"
        pppoe_data = get_pppoe_info(site, pppoe_key)

    # Prioritas 2: kalau tidak ketemu, baru cari berdasarkan nama
    if not pppoe_data:
        for candidate in pppoe_candidates(onu.get("name", "")):
            pppoe_data = get_pppoe_info(site, candidate)

            if pppoe_data:
                break

    name = clean_name(
        onu.get("name", "-")
    )

    description = clean_description(
        onu.get("description", "-")
    )

    status = format_status(
        detail.get("phase_state", "-")
    )

    quality = power_quality(
        power.get("onu_rx", "-")
    )

    ip = "-"
    pppoe_username = "-"
    pppoe_uptime = "-"
    pppoe_last_logout = "-"
    pppoe_status = "🔴 PPPoE OFFLINE"

    if pppoe_data:
        ip = pppoe_data.get("ip", "-")
        pppoe_username = pppoe_data.get("username", "-")
        pppoe_uptime = pppoe_data.get("uptime", "-")
        pppoe_last_logout = pppoe_data.get("last_logged_out", "-")

        if pppoe_data.get("status") == "active":
            pppoe_status = "🟢 PPPoE ACTIVE"
        else:
            pppoe_status = "🔴 PPPoE OFFLINE"

    message = (
        "👤 INFO PELANGGAN\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "👤 PELANGGAN\n"
        f"LOKASI : {site}\n"
        f"NAME   : {name}\n"
        f"IP     : {ip}\n"
        f"PPP    : {pppoe_status}\n"
        f"USER   : {pppoe_username}\n"
        f"UP     : {pppoe_uptime}\n"
        f"LAST   : {pppoe_last_logout}\n\n"

        "📡 ONU\n"
        f"ONU  : {interface}\n"
        f"PON  : {onu.get('pon', '-')}\n"
        f"ID   : {onu.get('onu_id', '-')}\n"
        f"DESC : {description}\n\n"

        "📶 STATUS\n"
        f"ONU   : {status}\n"
        f"CONFIG: {detail.get('config_state', '-')}\n"
        f"UPTIME: {detail.get('online_duration', '-')}\n\n"

        "📊 POWER\n"
        f"QUAL   : {quality}\n"
        f"ONU RX : {power.get('onu_rx', '-')} dBm\n"
        f"ONU TX : {power.get('onu_tx', '-')} dBm\n"
        f"OLT RX : {power.get('olt_rx', '-')} dBm\n"
        f"OLT TX : {power.get('olt_tx', '-')} dBm\n"

        "━━━━━━━━━━━━━━━━━━"
    )

    await message_obj.reply_text(
        message,
        reply_markup=main_menu()
    )


async def info_pelanggan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await deny_access(update)
        return

    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage:\n/info nama_pelanggan\n\nContoh:\n/info mudzakir"
        )
        return

    keyword = " ".join(context.args)

    onu_results = search_onu_cache(keyword)

    if not onu_results:
        await update.message.reply_text(
            f"❌ Pelanggan '{keyword}' tidak ditemukan.",
            reply_markup=main_menu()
        )
        return

    selected_onu, multiple_results = select_exact_onu(
        keyword,
        onu_results
    )

    if not selected_onu:
        INFO_SELECTIONS[user_id] = {
            "keyword": keyword,
            "results": multiple_results[:10]
        }

        await update.message.reply_text(
            format_multiple_onu_message(
                keyword,
                multiple_results
            ),
            reply_markup=build_selection_keyboard(
                multiple_results
            )
        )
        return

    await send_customer_info(
        update.message,
        keyword,
        selected_onu
    )


async def handle_info_selection(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    if data == "info_select_cancel":
        INFO_SELECTIONS.pop(user_id, None)

        await query.message.reply_text(
            "❌ Pemilihan pelanggan dibatalkan.",
            reply_markup=main_menu()
        )
        return

    if user_id not in INFO_SELECTIONS:
        await query.message.reply_text(
            "❌ Data pilihan sudah kadaluarsa.\nSilakan cari ulang.",
            reply_markup=main_menu()
        )
        return

    try:
        index = int(
            data.replace("info_select_", "")
        )
    except ValueError:
        await query.message.reply_text(
            "❌ Pilihan tidak valid.",
            reply_markup=main_menu()
        )
        return

    selection = INFO_SELECTIONS[user_id]
    results = selection["results"]
    keyword = selection["keyword"]

    if index < 0 or index >= len(results):
        await query.message.reply_text(
            "❌ Pilihan tidak ditemukan.",
            reply_markup=main_menu()
        )
        return

    selected_onu = results[index]

    INFO_SELECTIONS.pop(user_id, None)

    await send_customer_info(
        query.message,
        keyword,
        selected_onu
    )
