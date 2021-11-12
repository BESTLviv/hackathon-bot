from telebot.types import File
from telebot import TeleBot

import tempfile
import shutil
import os


class FileDownloader:
    MAX_SIZE = 50
    TEMP_FOLDER_PREFIX = "hack_bot_"

    file_folders: dict  # Dict{"subfolder_name": [file_id, file_id]}

    def __init__(self, bot: TeleBot, folders: dict):
        self.bot = bot

        self.file_folders = self._get_tg_files(folders)

    @property
    def _archive_chunks(self):
        pass

    def download_archives(self):
        with tempfile.TemporaryDirectory(
            prefix=self.TEMP_FOLDER_PREFIX
        ) as temp_dir_path:
            for folder_name, file_list in self.file_folders.items():
                self._create_subfolder(temp_dir_path, folder_name, file_list)

            archive_path = shutil.make_archive(f"CV_database", "zip", temp_dir_path)

    def _create_subfolder(self, dir_path: str, folder_name: str, file_list: list):
        folder_path = os.path.join(dir_path, folder_name)
        os.mkdir(folder_path)

        for tg_file in file_list:
            downloaded_file = self.bot.download_file(tg_file.file_path)
            downloaded_file_path = os.path.join(folder_path, tg_file.file_size)
            with open(downloaded_file_path, "wb") as new_file:
                new_file.write(downloaded_file)

    def _get_tg_files(self, file_id_folders: dict):
        file_folders = dict()

        for folder_name, file_id_list in file_id_folders.items():
            file_folders[folder_name] = list()

            for file_id in file_id_list:
                file_folders[folder_name].append(self.bot.get_file(file_id))

        return file_folders
