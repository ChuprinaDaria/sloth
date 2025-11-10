"""
Google Sheets Integration Service
Автоматичний експорт клієнтів, записів та статистики в Google Таблиці
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import connection
from django.conf import settings
import json


class GoogleSheetsService:
    """
    Сервіс для роботи з Google Sheets API
    """

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]

    # Шаблон структури таблиці
    TEMPLATE_STRUCTURE = {
        'clients': {
            'title': 'Клієнти',
            'headers': [
                'ID', 'Ім\'я', 'Телефон', 'Email', 'Перший візит',
                'Останній візит', 'Кількість візитів', 'Витрачено ₴',
                'Джерело', 'Теги/Нотатки'
            ],
            'column_widths': [60, 150, 120, 180, 120, 120, 100, 100, 120, 200]
        },
        'appointments': {
            'title': 'Записи',
            'headers': [
                'Дата', 'Час', 'Клієнт', 'Телефон', 'Послуга',
                'Майстер', 'Вартість ₴', 'Статус', 'Google Meet', 'Джерело'
            ],
            'column_widths': [100, 80, 150, 120, 150, 120, 100, 100, 250, 120]
        },
        'statistics': {
            'title': 'Статистика',
            'headers': [
                'Період', 'Записів', 'Нових клієнтів', 'Дохід ₴',
                'Топ послуга', 'Топ майстер', 'Conversion rate'
            ],
            'column_widths': [150, 100, 120, 100, 150, 120, 120]
        },
        'finances': {
            'title': 'Фінанси',
            'headers': ['Дата', 'Опис', 'Прибуток ₴', 'Витрати ₴', 'Баланс ₴'],
            'column_widths': [100, 250, 120, 120, 120]
        }
    }

    def __init__(self, credentials_dict):
        """
        Ініціалізація з credentials від OAuth
        
        credentials_dict має містити:
        - access_token
        - refresh_token (опціонально)
        - token_expiry (опціонально)
        """
        # Створюємо Credentials об'єкт напряму (як у GoogleCalendarService)
        # а не через from_authorized_user_info, який очікує client_id/client_secret
        self.credentials = Credentials(
            token=credentials_dict.get('access_token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=self.SCOPES
        )
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    @staticmethod
    def get_authorization_url(redirect_uri):
        """
        Генерує URL для OAuth авторизації (використовує той самий flow що Calendar)
        """
        from apps.integrations.google_calendar import GoogleCalendarService
        # Використовуємо OAuth від Calendar, додаємо Sheets scopes
        return GoogleCalendarService.get_authorization_url(
            redirect_uri,
            additional_scopes=GoogleSheetsService.SCOPES
        )

    def create_template_spreadsheet(self, organization_name):
        """
        Створює нову таблицю з шаблоном для салону

        Returns:
            dict: {'spreadsheet_id': '...', 'spreadsheet_url': '...'}
        """
        try:
            # Створюємо spreadsheet
            spreadsheet = {
                'properties': {
                    'title': f'Sloth - {organization_name}',
                    'locale': 'uk_UA',
                    'timeZone': 'Europe/Kiev'
                },
                'sheets': []
            }

            # Додаємо листи
            for sheet_key, sheet_data in self.TEMPLATE_STRUCTURE.items():
                sheet = {
                    'properties': {
                        'title': sheet_data['title'],
                        'gridProperties': {
                            'frozenRowCount': 1  # Закріпити header
                        }
                    }
                }
                spreadsheet['sheets'].append(sheet)

            # Створюємо таблицю
            result = self.sheets_service.spreadsheets().create(
                body=spreadsheet
            ).execute()

            spreadsheet_id = result['spreadsheetId']

            # Форматуємо кожен лист
            self._format_template_sheets(spreadsheet_id)

            return {
                'spreadsheet_id': spreadsheet_id,
                'spreadsheet_url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            }

        except HttpError as e:
            raise Exception(f"Error creating spreadsheet: {e}")

    def _format_template_sheets(self, spreadsheet_id):
        """
        Форматування шаблонних листів (headers, ширина колонок, формули)
        """
        requests = []
        sheet_id = 0

        for sheet_key, sheet_data in self.TEMPLATE_STRUCTURE.items():
            # Встановлюємо header values
            requests.append({
                'updateCells': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'rows': [{
                        'values': [
                            {
                                'userEnteredValue': {'stringValue': header},
                                'userEnteredFormat': {
                                    'backgroundColor': {'red': 0.2, 'green': 0.6, 'blue': 0.86},
                                    'textFormat': {
                                        'bold': True,
                                        'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}
                                    },
                                    'horizontalAlignment': 'CENTER'
                                }
                            }
                            for header in sheet_data['headers']
                        ]
                    }],
                    'fields': 'userEnteredValue,userEnteredFormat'
                }
            })

            # Встановлюємо ширину колонок
            for col_idx, width in enumerate(sheet_data['column_widths']):
                requests.append({
                    'updateDimensionProperties': {
                        'range': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': col_idx,
                            'endIndex': col_idx + 1
                        },
                        'properties': {
                            'pixelSize': width
                        },
                        'fields': 'pixelSize'
                    }
                })

            # Додаємо формули для Статистики листа
            if sheet_key == 'statistics':
                # Додаємо рядок з підсумками за поточний місяць
                current_month = datetime.now().strftime('%B %Y')
                requests.append({
                    'updateCells': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 1,
                            'endRowIndex': 2
                        },
                        'rows': [{
                            'values': [
                                {'userEnteredValue': {'stringValue': current_month}},
                                {'userEnteredValue': {'formulaValue': '=COUNTA(Записи!A2:A)'}},  # Кількість записів
                                {'userEnteredValue': {'formulaValue': '=COUNTIF(Клієнти!E2:E,">="&DATE(YEAR(TODAY()),MONTH(TODAY()),1))'}},  # Нові клієнти
                                {'userEnteredValue': {'formulaValue': '=SUM(Записи!G2:G)'}},  # Дохід
                                {'userEnteredValue': {'stringValue': '-'}},
                                {'userEnteredValue': {'stringValue': '-'}},
                                {'userEnteredValue': {'stringValue': '-'}}
                            ]
                        }],
                        'fields': 'userEnteredValue'
                    }
                })

            sheet_id += 1

        # Виконуємо всі запити
        if requests:
            self.sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={'requests': requests}
            ).execute()

    def export_clients(self, spreadsheet_id, clients_data):
        """
        Експорт клієнтів в лист "Клієнти"

        Args:
            spreadsheet_id: ID таблиці
            clients_data: list of dicts з даними клієнтів
        """
        try:
            # Формуємо рядки для експорту
            values = []
            for client in clients_data:
                row = [
                    client.get('id', ''),
                    client.get('name', ''),
                    client.get('phone', ''),
                    client.get('email', ''),
                    client.get('first_visit', ''),
                    client.get('last_visit', ''),
                    client.get('visit_count', 0),
                    client.get('total_spent', 0),
                    client.get('source', ''),
                    client.get('notes', '')
                ]
                values.append(row)

            # Очищаємо старі дані (крім header)
            self.sheets_service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range='Клієнти!A2:J'
            ).execute()

            # Додаємо нові дані
            body = {'values': values}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Клієнти!A2',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return result.get('updates', {}).get('updatedRows', 0)

        except HttpError as e:
            raise Exception(f"Error exporting clients: {e}")

    def export_appointments(self, spreadsheet_id, appointments_data):
        """
        Експорт записів в лист "Записи"
        """
        try:
            values = []
            for appt in appointments_data:
                row = [
                    appt.get('date', ''),
                    appt.get('time', ''),
                    appt.get('client_name', ''),
                    appt.get('client_phone', ''),
                    appt.get('service', ''),
                    appt.get('master', ''),
                    appt.get('price', 0),
                    appt.get('status', ''),
                    appt.get('meet_link', ''),
                    appt.get('source', '')
                ]
                values.append(row)

            # Очищаємо старі дані
            self.sheets_service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range='Записи!A2:J'
            ).execute()

            # Додаємо нові дані
            body = {'values': values}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Записи!A2',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return result.get('updates', {}).get('updatedRows', 0)

        except HttpError as e:
            raise Exception(f"Error exporting appointments: {e}")

    def append_client(self, spreadsheet_id, client_data):
        """
        Додає одного клієнта в кінець таблиці (для auto-export)
        """
        try:
            row = [[
                client_data.get('id', ''),
                client_data.get('name', ''),
                client_data.get('phone', ''),
                client_data.get('email', ''),
                client_data.get('first_visit', ''),
                client_data.get('last_visit', ''),
                client_data.get('visit_count', 0),
                client_data.get('total_spent', 0),
                client_data.get('source', ''),
                client_data.get('notes', '')
            ]]

            body = {'values': row}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Клієнти!A2',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return True

        except HttpError as e:
            print(f"Error appending client: {e}")
            return False

    def append_appointment(self, spreadsheet_id, appointment_data):
        """
        Додає один запис в кінець таблиці (для auto-export)
        """
        try:
            row = [[
                appointment_data.get('date', ''),
                appointment_data.get('time', ''),
                appointment_data.get('client_name', ''),
                appointment_data.get('client_phone', ''),
                appointment_data.get('service', ''),
                appointment_data.get('master', ''),
                appointment_data.get('price', 0),
                appointment_data.get('status', ''),
                appointment_data.get('meet_link', ''),
                appointment_data.get('source', '')
            ]]

            body = {'values': row}
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range='Записи!A2',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()

            return True

        except HttpError as e:
            print(f"Error appending appointment: {e}")
            return False

    def get_spreadsheet_info(self, spreadsheet_id):
        """
        Отримує інформацію про таблицю
        """
        try:
            spreadsheet = self.sheets_service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()

            return {
                'title': spreadsheet['properties']['title'],
                'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}",
                'sheets': [sheet['properties']['title'] for sheet in spreadsheet['sheets']]
            }

        except HttpError as e:
            raise Exception(f"Error getting spreadsheet info: {e}")


class SheetsExportHelper:
    """
    Helper для підготовки даних для експорту в Sheets
    """

    @staticmethod
    def prepare_clients_export(tenant_schema):
        """
        Підготовка даних клієнтів для експорту
        """
        from apps.agent.models import Conversation, Message

        # Переключаємося на tenant schema
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {tenant_schema}, public")

        # Отримуємо всі унікальні клієнти з розмов
        conversations = Conversation.objects.all()

        clients_data = []
        client_phones = set()

        for conv in conversations:
            # Унікальність по телефону/джерелу
            client_key = f"{conv.phone_number}_{conv.source}"
            if client_key in client_phones:
                continue
            client_phones.add(client_key)

            # Підраховуємо кількість повідомлень від клієнта
            messages = conv.messages.filter(role='user')

            # Перший та останній візит
            first_message = messages.order_by('created_at').first()
            last_message = messages.order_by('created_at').last()

            client_data = {
                'id': conv.id,
                'name': conv.client_name or 'Невідомий',
                'phone': conv.phone_number or '',
                'email': conv.email or '',
                'first_visit': first_message.created_at.strftime('%Y-%m-%d %H:%M') if first_message else '',
                'last_visit': last_message.created_at.strftime('%Y-%m-%d %H:%M') if last_message else '',
                'visit_count': messages.count(),
                'total_spent': 0,  # TODO: інтеграція з платежами
                'source': conv.source or 'unknown',
                'notes': ''
            }

            clients_data.append(client_data)

        return clients_data

    @staticmethod
    def prepare_appointments_export(tenant_schema, days_back=30):
        """
        Підготовка даних записів для експорту (з календаря)
        """
        from apps.integrations.models import Integration
        from apps.integrations.google_calendar import GoogleCalendarService

        # Переключаємося на tenant schema
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {tenant_schema}, public")

        # Знаходимо Google Calendar інтеграцію
        try:
            integration = Integration.objects.get(integration_type='google_calendar', status='active')
            credentials = integration.get_credentials()

            calendar_service = GoogleCalendarService(credentials)

            # Отримуємо події за останні N днів
            start_date = timezone.now() - timedelta(days=days_back)

            # TODO: Реалізувати метод get_events в GoogleCalendarService
            # events = calendar_service.get_events(start_date)

            # Поки повертаємо пустий список
            return []

        except Integration.DoesNotExist:
            # Немає інтеграції з календарем
            return []
