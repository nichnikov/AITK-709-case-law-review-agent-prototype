import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# --- Google Sheets ---
# URL вашей таблицы
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1n0avONQkCPiH-fv55H1L45WdzSKjoEVIbxfUcQU8KLY/edit?gid=0#gid=0"
# Имя файла с ключами доступа
CREDENTIALS_FILE = "credentials.json"
# Области доступа для API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]

# --- OpenAI GPT ---
# Ваш API ключ из .env файла
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Web Scraper ---
# Папка для сохранения текстов судебных актов
TEXTS_DIR = "texts"

# --- Логика обработки ---
# Название столбца, где находятся ссылки
SOURCE_COLUMN = "Реквизиты"
# Название столбца, куда нужно добавить результат
TARGET_COLUMN = "Оглавление" # Пример, измените на нужный столбец
# Название столбца, по которому определяем, что строка обработана
STATUS_COLUMN = "Стадия"
PROCESSED_STATUS_TEXT = "Обработано"

# Промпт для GPT модели
# {text} будет заменено на текст судебного акта
GPT_PROMPT_TEMPLATE = """
Проанализируй следующий текст судебного акта. На основе анализа, составь краткое оглавление или саммари ключевых частей документа.

Текст акта:
---
{text}
---

Результат представь в виде структурированного списка.
"""