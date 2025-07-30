Ниже представлена полная структура проекта, код для каждого файла и подробная инструкция по настройке и запуску.

1. Структура проекта
Создайте следующую структуру папок и файлов. Это поможет организовать код и сделать его поддерживаемым.


judicial_analyzer/
├── .env
├── .gitignore
├── config.py
├── gpt_processor.py
├── google_sheets_handler.py
├── main.py
├── requirements.txt
├── web_scraper.py
└── texts/
    └── (здесь будут сохраняться .txt файлы)
2. Настройка окружения и зависимостей
Шаг 1: Установка библиотек
Сначала установим все необходимые Python библиотеки. Создайте файл requirements.txt и добавьте в него следующие строки:

requirements.txt


gspread
oauth2client
requests
beautifulsoup4
openai
python-dotenv
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
Затем выполните в терминале команду для установки:


pip install -r requirements.txt
Шаг 2: Настройка доступа к Google Sheets API
Создайте проект в Google Cloud Console:
Перейдите на Google Cloud Console.
Создайте новый проект (например, "Judicial Analyzer").
Включите API:
В меню навигации выберите "APIs & Services" -> "Library".
Найдите и включите "Google Sheets API" и "Google Drive API".
Создайте сервисный аккаунт:
Перейдите в "APIs & Services" -> "Credentials".
Нажмите "Create Credentials" -> "Service account".
Дайте ему имя (например, sheets-editor) и нажмите "Create and Continue".
На шаге "Grant this service account access to project" выберите роль "Editor" и нажмите "Continue", затем "Done".
Получите JSON-ключ:
На странице "Credentials" найдите созданный сервисный аккаунт и кликните по нему.
Перейдите на вкладку "KEYS".
Нажмите "ADD KEY" -> "Create new key".
Выберите "JSON" и нажмите "Create". Файл с ключом (например, project-name-12345.json) будет скачан на ваш компьютер.
Переименуйте и разместите ключ:
Переименуйте скачанный файл в credentials.json.
Поместите файл credentials.json в корень вашего проекта (judicial_analyzer/).
Предоставьте доступ к Google Таблице:
Откройте ваш credentials.json и скопируйте email сервисного аккаунта (поле client_email). Он выглядит примерно так: sheets-editor@project-name-12345.iam.gserviceaccount.com.
Откройте вашу Google Таблицу.
Нажмите "Настройки доступа" (Share) в правом верхнем углу.
Вставьте email сервисного аккаунта в поле для добавления пользователей и дайте ему права "Редактор" (Editor).
Шаг 3: Настройка API для GPT-модели
Сервис будет использовать API от OpenAI. Если у вас другой провайдер, логика останется той же, нужно будет лишь изменить код в gpt_processor.py.

Получите API ключ: Зарегистрируйтесь на платформе OpenAI и получите свой API ключ.
Сохраните ключ: Создайте файл .env в корне проекта и добавьте в него ваш ключ.
.env


OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
Шаг 4: Файл .gitignore
Чтобы случайно не загрузить ваши секретные ключи в систему контроля версий (например, Git), создайте файл .gitignore.

.gitignore


# Python
__pycache__/
*.pyc

# Environment
.env

# Credentials
credentials.json

# Data
texts/
3. Код скриптов
Теперь напишем код для каждого модуля.

config.py
Этот файл будет хранить все конфигурационные данные.


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
google_sheets_handler.py
Модуль для всей работы с Google Sheets: чтение и запись данных.


import gspread
from oauth2client.service_account import ServiceAccountCredentials
import config

class GoogleSheetHandler:
    def __init__(self):
        """Инициализация и авторизация в Google Sheets."""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                config.CREDENTIALS_FILE, config.SCOPES
            )
            client = gspread.authorize(creds)
            self.sheet = client.open_by_url(config.GOOGLE_SHEET_URL).sheet1
            print("✓ Успешная авторизация в Google Sheets.")
        except Exception as e:
            print(f"✗ Ошибка авторизации в Google Sheets: {e}")
            raise

    def get_all_records(self):
        """Получает все записи из листа."""
        return self.sheet.get_all_records()

    def update_cell(self, row_index, col_index, value):
        """Обновляет значение в конкретной ячейке."""
        self.sheet.update_cell(row_index, col_index, value)
        print(f"  -> Ячейка ({row_index}, {col_index}) обновлена.")

    def get_headers(self):
        """Возвращает заголовки столбцов."""
        return self.sheet.row_values(1)
web_scraper.py
Модуль для извлечения текста с веб-страниц.


import requests
from bs4 import BeautifulSoup
import os
import re
from config import TEXTS_DIR

def scrape_text_from_url(url: str, file_name: str) -> str:
    """
    Извлекает текст судебного акта со страницы и сохраняет его в .txt файл.

    Args:
        url (str): Ссылка на страницу с актом.
        file_name (str): Имя для сохраняемого файла.

    Returns:
        str: Извлеченный текст или пустая строка в случае ошибки.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        print(f"  -> Загрузка страницы: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Проверка на ошибки HTTP (4xx, 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # !!! ВАЖНО: Этот селектор нужно адаптировать под конкретный сайт!
        # С помощью инструментов разработчика в браузере (F12) найдите тег,
        # который содержит основной текст документа.
        # Пример для сайта sudact.ru - текст находится в <div id="doc_text">
        content_div = soup.find('div', id='doc_text')
        
        if not content_div:
            # Попробуем другой общий селектор, если первый не сработал
            content_div = soup.find('div', class_='doc-text')

        if not content_div:
            print(f"  ✗ Не удалось найти основной блок текста на странице {url}. Пропускаем.")
            return ""

        text = content_div.get_text(separator='\n', strip=True)

        # Сохранение текста в файл
        if not os.path.exists(TEXTS_DIR):
            os.makedirs(TEXTS_DIR)

        # Очистка имени файла от недопустимых символов
        safe_file_name = re.sub(r'[\\/*?:"<>|]', "", file_name)
        file_path = os.path.join(TEXTS_DIR, f"{safe_file_name}.txt")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"  -> Текст сохранен в файл: {file_path}")

        return text

    except requests.RequestException as e:
        print(f"  ✗ Ошибка при запросе к {url}: {e}")
        return ""
    