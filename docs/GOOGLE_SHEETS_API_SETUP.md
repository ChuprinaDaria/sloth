# Налаштування Google Sheets API

## Проблема
При спробі підключення Google Sheets інтеграції виникає помилка:
```
Error creating spreadsheet: <HttpError 403 when requesting https://sheets.googleapis.com/v4/spreadsheets?alt=json returned "Google Sheets API has not been used in project 513024215665 before or it is disabled."
```

## Рішення

### 1. Відкрийте Google Cloud Console
Перейдіть за посиланням з помилки або використайте:
```
https://console.developers.google.com/apis/api/sheets.googleapis.com/overview?project=513024215665
```

### 2. Увійдіть в обліковий запис
Використайте той же Google обліковий запис, що й для OAuth credentials.

### 3. Активуйте Google Sheets API
1. Натисніть кнопку **"Enable"** (Активувати)
2. Зачекайте декілька секунд, поки API активується
3. Перевірте, що статус змінився на "Enabled"

### 4. Додайте інші необхідні API (якщо потрібно)
Переконайтеся, що активовані наступні API:
- ✅ Google Calendar API (для календаря)
- ✅ Google Sheets API (для таблиць)
- ✅ Google My Business API (для відгуків)

### 5. Перевірте налаштування
1. Зайдіть в **APIs & Services > Credentials**
2. Переконайтеся, що OAuth 2.0 Client ID налаштований правильно
3. Перевірте, що у **Authorized redirect URIs** є:
   ```
   https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
   ```

### 6. Зачекайте 2-5 хвилин
Після активації API потрібен час для поширення змін у системах Google.

### 7. Спробуйте знову підключити Google Sheets
Поверніться на сторінку інтеграцій та повторіть підключення.

## Примітка
Якщо помилка повторюється після активації:
1. Перевірте, що ви увійшли в правильний Google обліковий запис
2. Переконайтеся, що проект `513024215665` має правильні налаштування
3. Зачекайте ще декілька хвилин
4. Очистіть кеш браузера та спробуйте знову

## Додаткова інформація
- [Google Sheets API Documentation](https://developers.google.com/sheets/api)
- [Google Cloud Console](https://console.cloud.google.com/)

