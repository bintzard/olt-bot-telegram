import logging


async def global_error_handler(update, context):

    error = context.error

    logging.error(f"Error : {error}")

    if update and update.effective_message:

        await update.effective_message.reply_text(
            "❌ Terjadi kesalahan saat mengambil data OLT.\n"
            "Silakan coba beberapa saat lagi."
        )
