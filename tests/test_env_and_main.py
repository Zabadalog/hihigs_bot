import unittest
import os
import importlib.util

class TestEnvAndMain(unittest.TestCase):
    def test_env_file_exists(self):
        self.assertTrue(os.path.exists(".env"), "Файл .env не найден в корне проекта")

    def test_logs_folder_exists(self):
        self.assertTrue(os.path.isdir("logs"), "Папка logs не найдена")

    def test_main_function_exists(self):
        spec = importlib.util.spec_from_file_location("bot", "bot.py")
        bot = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(bot)

        self.assertTrue(hasattr(bot, "main"), "Функция main() не найдена в bot.py")
