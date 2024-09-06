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

logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv("BOT_TOKEN", "too sad for you :(")
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://dmeckers.github.io/cream-front/")
BOT_SUPERADMIN_ID = int(os.getenv("BOT_SUPERADMIN_ID", 0))

# Global variables
stations = ["cream"]

async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome",
        reply_markup=ReplyKeyboardMarkup(
            [
                [
                    KeyboardButton(
                        "Open Web App",
                        web_app=WebAppInfo(WEB_APP_URL),
                    )
                ]
            ],
            resize_keyboard=True,
        ),
    )

# Handlers
async def text_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message_text = update.message.text
    match_add = re.match(r"^<(.+)>$", message_text)
    match_remove = re.match(r"^>(.+)<$", message_text)

    if match_add:
        station_name = match_add.group(1)
        stations.append(station_name)
        await update.message.reply_text(f"Station {station_name} has been created.")
        return

    if match_remove:
        station_name = match_remove.group(1)
        if station_name in stations:
            stations.remove(station_name)
            await update.message.reply_text(f"Station {station_name} has been removed.")
        else:
            await update.message.reply_text(f"Station {station_name} does not exist.")
        return

    await update.message.reply_text(
        "Wassup ma nigga, hope u doin good. I'm just a fucking piece of hardcoded message. Hit the button below to open the radio.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Open Web App", web_app=WebAppInfo(WEB_APP_URL))]],
            resize_keyboard=True,
        ),
    )


async def audio_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    domain = "https://cream-api"

    sender_id = update.message.from_user.id
    if sender_id != BOT_SUPERADMIN_ID:
        return await context.message.reply_text(
            "Only superadmin can upload audio files.505ATb"
        )

    try:
        [local_file_path, file_name] = await TgBotHelpers.download_audio_file(
            update=update, context=context
        )

        with open(local_file_path, "rb") as file:
            files = {"file": (file_name, file)}

            response = requests.post(
                f"{domain}/api/v1/tracks",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {os.getenv('JWT_TOKEN')}",
                },
                files=files,
                verify=False,
            )

            os.remove(local_file_path)

            if response.status_code == 201:
                await update.message.reply_text("Audio has been uploaded.")
            else:
                await update.message.reply_text("Error when uploading file")
                logger.error(
                    f"Upload failed with status {response.status_code}: {response.text}"
                )
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        await update.message.reply_text(f"Error when uploading file {str(e)}")


def main() -> None:

    if not os.getenv("JWT_TOKEN"):
        raise Exception("JWT_TOKEN is not set")

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
    )
    application.add_handler(MessageHandler(filters.AUDIO, audio_message_handler))
    application.add_handler(CommandHandler("start", start_command_handler))

    application.run_polling()


if __name__ == "__main__":
    main()
