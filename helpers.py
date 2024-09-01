import os
import requests
from pathlib import Path
from urllib.parse import urlparse


class TgBotHelpers:

    @staticmethod
    async def download_audio_file(update, context) -> dict:
        """
        Downloads an audio file from Telegram and saves it locally.

        :param update: Telegram update object
        :param context: Telegram context
        :returns: Dictionary with local file path and file name
        """
        audio = update.message.audio
        file_id = audio.file_id

        file_name = audio.file_name if audio.file_name else "audio"

        # Resolve the directory of the current script
        current_dir = Path(__file__).resolve().parent
        downloads_dir = current_dir / "downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)

        # Get file information from Telegram
        file_info = await context.bot.get_file(file_id)
        download_url = file_info.file_path
        file_extension = Path(urlparse(download_url).path).suffix
        # file_name = f"{title}{file_extension}"

        # Construct the full file path
        local_file_path = downloads_dir / file_name

        print(f"Download URL: {download_url}")
        print(f"Saving file to: {local_file_path}")

        # Download the file
        response = requests.get(download_url, stream=True)

        if response.status_code == 200:
            # Write the content to a file
            with open(local_file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return [local_file_path.as_posix(), file_name]
        else:
            print(
                f"Failed to download file. Status code: {response.status_code}, Response text: {response.text}"
            )
            response.raise_for_status()
