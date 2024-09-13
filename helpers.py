import os
from time import sleep
import requests
from pathlib import Path
from urllib.parse import urlparse


class TgBotHelpers:

    _SERVICE_NAME = "TgBotService"
    _TOKEN_KEY = "jwt_token"
    _SERVER_DOMAIN = "https://cream-api"
    _TOKEN_FILE_PATH = Path(__file__).resolve().parent / "jwt_token.txt"

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

    @staticmethod
    def login_on_401_and_upload_file(file_name, file, local_file_path):
        token = TgBotHelpers.getOrFetchJwtToken()
        headers = {
            "Accept": "/json",
            "Authorization": f"Bearer {token}",
        }

        files = {"file": (file_name, file)}

        try:
            requests.post(
                f"{TgBotHelpers._SERVER_DOMAIN}/api/v1/tracks",
                headers=headers,
                files=files,
                verify=False,
            )
        except Exception as e:
            os.remove(local_file_path)
            raise e

        os.remove(local_file_path)

    @staticmethod
    def getOrFetchJwtToken() -> str:
        """
        Fetches the JWT token from the text file or fetches a new one from the server.
        :returns: JWT token
        :raises Exception: If the login fails
        """
        if TgBotHelpers._TOKEN_FILE_PATH.exists():
            with open(TgBotHelpers._TOKEN_FILE_PATH, "r") as token_file:
                token = token_file.read().strip()
                if token:
                    return token

        response = requests.post(
            f"{TgBotHelpers._SERVER_DOMAIN}/api/login",
            json={
                "email": os.getenv("BOT_WORKER_EMAIL"),
                "password": os.getenv("BOT_WORKER_PASSWORD"),
            },
            verify=False,
        )

        if response.status_code != 200 and response.status_code != 201:
            raise Exception("Failed to login")

        new_token = response.json()["token"]

        with open(TgBotHelpers._TOKEN_FILE_PATH, "w") as token_file:
            token_file.write(new_token)

        return new_token
