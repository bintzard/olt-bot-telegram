import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from services.olt import check_olt


async def olt_status(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "⏳ Checking OLT..."
    )

    result = await asyncio.to_thread(
        check_olt
    )

    if not result:

        result = "No response from OLT"

    await update.message.reply_text(
        result
)
