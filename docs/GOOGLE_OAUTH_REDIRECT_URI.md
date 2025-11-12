# Налаштування Google OAuth Redirect URI

## Проблема: `redirect_uri_mismatch`

Якщо ви отримуєте помилку **"Error 400: redirect_uri_mismatch"**, це означає, що redirect URI в коді не збігається з тим, що зареєстровано в Google Cloud Console.

## Рішення

### 1. Визначте ваш BACKEND_URL

Перевірте значення `BACKEND_URL` у вашому `.env` файлі:

```bash
# На сервері
cat /opt/sloth/backend/.env | grep BACKEND_URL
```

Або в Docker:
```bash
docker compose exec backend env | grep BACKEND_URL
```

**Приклад:**
- `BACKEND_URL=https://sloth-ai.lazysoft.pl` (БЕЗ слешу в кінці!)
- або `BACKEND_URL=https://api.sloth-ai.lazysoft.pl`

### 2. Додайте Redirect URI в Google Cloud Console

1. Відкрийте [Google Cloud Console](https://console.cloud.google.com/)
2. Виберіть ваш проект
3. Перейдіть до **APIs & Services** → **Credentials**
4. Знайдіть ваш **OAuth 2.0 Client ID** (або створіть новий)
5. Натисніть **Edit** (редагувати)
6. У розділі **Authorized redirect URIs** додайте:

#### Для Google Calendar:
```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
```

#### Для Google Sheets:
```
https://sloth-ai.lazysoft.pl/api/integrations/sheets/callback/
```

#### Для Google My Business:
```
https://sloth-ai.lazysoft.pl/api/integrations/google-reviews/callback/
```

**⚠️ ВАЖЛИВО:**
- URI повинен точно збігатися (включаючи слеш в кінці `/`)
- Використовуйте `https://` (не `http://`)
- Переконайтеся, що немає подвійних слешів (`//`)

### 3. Якщо ви використовуєте локальну розробку:

Для локальної розробки додайте:
```
http://localhost:8000/api/integrations/calendar/callback/
http://localhost:8000/api/integrations/sheets/callback/
```

### 4. Перевірка

Після додавання redirect URI:

1. **Збережіть зміни** в Google Cloud Console
2. **Зачекайте 1-2 хвилини** (Google може кешувати налаштування)
3. **Спробуйте підключити інтеграцію знову**

### 5. Якщо проблема залишається

Перевірте логи бекенду, щоб побачити який саме redirect_uri використовується:

```bash
# В Docker
docker compose logs backend | grep redirect_uri
```

Або перевірте в коді, який URL формується:
- `backend/apps/integrations/views.py` - функція `calendar_auth_url()`
- Переконайтеся, що `BACKEND_URL` в `.env` правильний

### Приклад правильної конфігурації

**`.env` файл:**
```env
BACKEND_URL=https://sloth-ai.lazysoft.pl
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Google Cloud Console → Authorized redirect URIs:**
```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
https://sloth-ai.lazysoft.pl/api/integrations/sheets/callback/
```

### Додаткова інформація

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Redirect URI Validation](https://developers.google.com/identity/protocols/oauth2/policies#uri-validation)

