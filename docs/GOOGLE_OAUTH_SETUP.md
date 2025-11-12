# Правильна конфігурація Google OAuth

## ❌ ЩО НЕПРАВИЛЬНО:

Ви додали в **Authorized redirect URIs**:
1. `https://www.googleapis.com/auth/calendar` ❌ - це **SCOPE** (дозвіл), не redirect URI
2. `https://www.googleapis.com/auth/calendar.events` ❌ - це **SCOPE**, не redirect URI  
3. `https://www.googleapis.com/auth/spreadsheets` ❌ - це **SCOPE**, не redirect URI
4. `https://sloth-ai.lazysoft.pl/api/integrations/google-reviews/callback/` ❌ - такого endpoint не існує
5. `https://sloth-ai.lazysoft.pl/api/integrations/sheets/callback/` ❌ - такого endpoint не існує

## ✅ ЩО ПРАВИЛЬНО:

### 1. Authorized redirect URIs (в Google Cloud Console)

Додайте **ТІЛЬКИ ОДИН** redirect URI:

```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
```

**Чому один?** 
- Google Calendar, Google Sheets та Google My Business використовують **один і той самий OAuth flow**
- Всі вони використовують callback endpoint: `/api/integrations/calendar/callback/`

### 2. OAuth Scopes (дозволи)

Scopes налаштовуються в **коді**, а не в Google Cloud Console. Вони автоматично додаються до запиту авторизації.

Поточні scopes в коді:
- `https://www.googleapis.com/auth/calendar` - для Calendar
- `https://www.googleapis.com/auth/calendar.events` - для Calendar events
- `https://www.googleapis.com/auth/spreadsheets` - для Sheets
- `https://www.googleapis.com/auth/business.manage` - для Google My Business

## 📋 Інструкція для Google Cloud Console:

1. Відкрийте [Google Cloud Console](https://console.cloud.google.com/)
2. Виберіть ваш проект
3. Перейдіть: **APIs & Services** → **Credentials**
4. Знайдіть ваш **OAuth 2.0 Client ID** → натисніть **Edit**
5. У розділі **"Authorized redirect URIs"**:
   - **Видаліть** всі неправильні URI (scopes та неіснуючі endpoints)
   - **Додайте** тільки один:
     ```
     https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
     ```
6. **Збережіть** зміни

## 🔍 Перевірка:

Після збереження, ваш список **Authorized redirect URIs** має містити тільки:

```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
```

## ⚠️ Важливо:

- **Redirect URI** має точно збігатися (включаючи слеш `/` в кінці)
- Використовуйте `https://` (не `http://`)
- Переконайтеся що немає подвійних слешів (`//`)

## 📝 Як це працює:

1. **Google Calendar** → використовує `/api/integrations/calendar/callback/`
2. **Google Sheets** → використовує той самий OAuth flow (той самий callback)
3. **Google My Business** → використовує той самий OAuth flow (той самий callback)

Всі три інтеграції використовують **один OAuth Client ID** та **один redirect URI**.

