from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from dotenv import load_dotenv

import os

from handlers.start import start
from handlers.olt import olt_status
from handlers.onu import onu_status
from handlers.refresh_onu import refresh_onu
from handlers.detail import detail_onu
from handlers.power import power_onu
from handlers.callback import button_callback
from handlers.text_input import handle_text_input
from handlers.error_handler import global_error_handler
from handlers.myid import my_id
from handlers.user_admin import add_user, remove_user, list_users
from handlers.info import info_pelanggan


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)


# COMMAND


app.add_handler(CommandHandler("adduser", add_user))
app.add_handler(CommandHandler("removeuser", remove_user))
app.add_handler(CommandHandler("users", list_users))


app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("olt", olt_status)
)

app.add_handler(
    CommandHandler("onu", onu_status)
)

app.add_handler(
    CommandHandler("refresh_onu", refresh_onu)
)

app.add_handler(
    CommandHandler("detail", detail_onu)
)

app.add_handler(
    CommandHandler("power", power_onu)
)

app.add_handler(
    CommandHandler("myid", my_id)
)

app.add_handler(
    CommandHandler("info", info_pelanggan)
)

# BUTTON CALLBACK

app.add_handler(
    CallbackQueryHandler(button_callback)
)


# TEXT INPUT

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_input
    )
)


# ERROR HANDLER

app.add_error_handler(
    global_error_handler
)


print("Bot running...")


app.run_polling()
