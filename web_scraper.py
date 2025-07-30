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