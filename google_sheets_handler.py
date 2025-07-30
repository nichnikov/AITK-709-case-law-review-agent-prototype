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