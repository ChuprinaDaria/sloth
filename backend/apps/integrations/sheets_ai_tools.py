"""
Google Sheets AI Tools
Інструменти для AI агента для роботи з Google Sheets
"""

from apps.integrations.google_sheets import GoogleSheetsService, SheetsExportHelper
from apps.integrations.models import Integration
from datetime import datetime, timedelta
import json


class SheetsAITools:
    """
    AI інструменти для роботи з Google Sheets через команди в чаті
    """

    def __init__(self, tenant_schema):
        self.tenant_schema = tenant_schema
        self.integration = self._get_integration()

    def _get_integration(self):
        """Отримує активну Google Sheets інтеграцію"""
        try:
            return Integration.objects.get(
                integration_type='google_sheets',
                is_active=True
            )
        except Integration.DoesNotExist:
            return None

    def export_all_clients(self):
        """
        AI команда: "експортуй всіх клієнтів в таблицю"

        Returns:
            str: Повідомлення для користувача
        """
        if not self.integration:
            return "❌ Google Sheets не підключено. Підключіть інтеграцію в налаштуваннях."

        try:
            credentials = self.integration.get_credentials()
            sheets_service = GoogleSheetsService(credentials)

            # Отримуємо spreadsheet_id з налаштувань
            config = self.integration.config or {}
            spreadsheet_id = config.get('spreadsheet_id')

            if not spreadsheet_id:
                return "❌ Таблиця не налаштована. Створіть таблицю в налаштуваннях інтеграції."

            # Підготовка даних
            clients_data = SheetsExportHelper.prepare_clients_export(self.tenant_schema)

            # Експорт
            updated_rows = sheets_service.export_clients(spreadsheet_id, clients_data)

            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

            return f"✅ Експортовано {updated_rows} клієнтів в Google Sheets!\n\n📊 Відкрити таблицю: {spreadsheet_url}"

        except Exception as e:
            return f"❌ Помилка експорту: {str(e)}"

    def export_recent_appointments(self, days=30):
        """
        AI команда: "експортуй записи за останній місяць"

        Args:
            days: Кількість днів назад

        Returns:
            str: Повідомлення для користувача
        """
        if not self.integration:
            return "❌ Google Sheets не підключено."

        try:
            credentials = self.integration.get_credentials()
            sheets_service = GoogleSheetsService(credentials)

            config = self.integration.config or {}
            spreadsheet_id = config.get('spreadsheet_id')

            if not spreadsheet_id:
                return "❌ Таблиця не налаштована."

            # Підготовка даних
            appointments_data = SheetsExportHelper.prepare_appointments_export(
                self.tenant_schema,
                days_back=days
            )

            # Експорт
            updated_rows = sheets_service.export_appointments(spreadsheet_id, appointments_data)

            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

            return f"✅ Експортовано {updated_rows} записів за останні {days} днів!\n\n📊 Відкрити таблицю: {spreadsheet_url}"

        except Exception as e:
            return f"❌ Помилка експорту: {str(e)}"

    def get_spreadsheet_link(self):
        """
        AI команда: "покажи посилання на таблицю"
        """
        if not self.integration:
            return "❌ Google Sheets не підключено."

        config = self.integration.config or {}
        spreadsheet_id = config.get('spreadsheet_id')

        if not spreadsheet_id:
            return "❌ Таблиця не налаштована."

        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        return f"📊 Ваша Google таблиця:\n{spreadsheet_url}"

    def check_sheets_status(self):
        """
        Перевірка статусу інтеграції
        """
        if not self.integration:
            return "❌ Google Sheets не підключено. Підключіть у налаштуваннях."

        config = self.integration.config or {}
        spreadsheet_id = config.get('spreadsheet_id')
        auto_export = config.get('auto_export_enabled', False)

        if not spreadsheet_id:
            return "⚠️ Google Sheets підключено, але таблиця не створена. Створіть таблицю в налаштуваннях."

        spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

        status_message = f"""
✅ Google Sheets активний

📊 Таблиця: {spreadsheet_url}
🔄 Автоматичний експорт: {'Увімкнено' if auto_export else 'Вимкнено'}

Доступні команди:
- "експортуй клієнтів" - експорт всіх клієнтів
- "експортуй записи" - експорт записів за місяць
- "покажи таблицю" - отримати посилання
"""

        return status_message.strip()


# Функції для OpenAI Function Calling
def get_sheets_functions_definitions():
    """
    Визначення функцій для OpenAI Function Calling
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "export_clients_to_sheets",
                "description": "Експортує всіх клієнтів в Google Sheets таблицю. Використовуй коли користувач просить експортувати клієнтів, створити список клієнтів, або показати базу клієнтів.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "export_appointments_to_sheets",
                "description": "Експортує записи в Google Sheets. Використовуй коли користувач просить експортувати записи, показати статистику записів, або створити звіт.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days": {
                            "type": "integer",
                            "description": "За скільки днів назад експортувати записи (за замовчуванням 30)",
                            "default": 30
                        }
                    },
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_sheets_link",
                "description": "Отримує посилання на Google Sheets таблицю. Використовуй коли користувач просить показати таблицю або дати посилання.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]
