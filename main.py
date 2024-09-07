import os
import logging
from pathlib import Path
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from telegram.ext import CallbackQueryHandler
from helpers import TgBotHelpers
import re

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv("BOT_TOKEN", "too sad for you :(")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://dmeckers.github.io/cream-front/")
BOT_SUPERADMIN_ID = int(os.getenv("BOT_SUPERADMIN_ID", 0))

BOT_WORKER_EMAIL = os.getenv("BOT_WORKER_EMAIL", "cream_radio_bot")
BOT_WORKER_PASSWORD = os.getenv("BOT_WORKER_PASSWORD", "cream_radio_bot")
stations = ["cream"]


async def defaultGreetings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Cream Radio! Hit the button below to open the radio.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Open Web App", web_app=WebAppInfo(WEB_APP_URL))]],
            resize_keyboard=True,
        ),
    )


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await defaultGreetings(update, context)


async def text_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await defaultGreetings(update, context)


async def audio_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    sender_id = update.message.from_user.id

    if sender_id != BOT_SUPERADMIN_ID:
        return await context.message.reply_text("Ti ohuel")

    try:
        [local_file_path, file_name] = await TgBotHelpers.download_audio_file(
            update=update, context=context
        )

        with open(local_file_path, "rb") as file:
            TgBotHelpers.login_on_401_and_upload_file(file_name, file, local_file_path)

        await update.message.reply_text("Audio has been uploaded.")

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        await update.message.reply_text(f"Error when uploading file {str(e)}")


def main() -> None:

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
    )
    application.add_handler(MessageHandler(filters.AUDIO, audio_message_handler))
    application.add_handler(CommandHandler("start", start_command_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
