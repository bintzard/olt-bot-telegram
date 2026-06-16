from telegram import Update
from telegram.ext import ContextTypes

from handlers.callback import USER_STATE

from handlers.onu import onu_status
from handlers.detail import detail_onu
from handlers.power import power_onu
from utils.security import is_user_allowed, deny_access
from handlers.info import info_pelanggan


async def handle_text_input(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if not is_user_allowed(user_id):
        await deny_access(update)
        return

    user_id = update.effective_user.id

    if user_id not in USER_STATE:
        return

    state = USER_STATE[user_id]

    text = update.message.text

    # ubah input text menjadi args
    context.args = text.split()

    # Cari ONU

    if state == "cari_onu":

        await onu_status(
            update,
            context
        )

    # Detail ONU

    elif state == "detail_onu":

        await detail_onu(
            update,
            context
        )

    # Power ONU

    elif state == "power_onu":

        await power_onu(
            update,
            context
        )

    # Detail Pelanggan
    elif state == "info_pelanggan":

        await info_pelanggan(
            update,
            context
        )

    # reset state setelah selesai

    USER_STATE.pop(user_id, None)
