# 🔧 Виправлення Telegram та Google OAuth - Покрокова інструкція

## ⚠️ Проблеми що потрібно виправити:

1. ❌ **Telegram: 500 Internal Server Error**
2. ❌ **Google OAuth: redirect_uri_mismatch**

---

## 📦 Крок 1: Оновіть код на сервері

```bash
cd /opt/sloth
git pull origin claude/setup-fernet-key-telegram-011CUyxnr17s2UCD1QcWgygB
```

**Що це виправить:**
- Telegram async context errors
- Instagram webhook errors
- Додасть GOOGLE_OAUTH_SETUP.md гайд

---

## 🔐 Крок 2: Налаштуйте Google OAuth ПРАВИЛЬНО

### 2.1 Перевірте BACKEND_URL на сервері:

```bash
cat /opt/sloth/backend/.env | grep BACKEND_URL
```

**Має бути ТОЧНО:**
```bash
BACKEND_URL=https://sloth-ai.lazysoft.pl
```

⚠️ **БЕЗ слешу `/` в кінці!**

Якщо немає або неправильний - виправте:
```bash
nano /opt/sloth/backend/.env
```

### 2.2 Відкрийте Google Cloud Console

1. Перейдіть: https://console.cloud.google.com/
2. Виберіть ваш проект
3. Меню зліва: **APIs & Services** → **Credentials**
4. Знайдіть ваш **OAuth 2.0 Client ID**
5. Натисніть на назву для редагування

### 2.3 Налаштуйте URIs (ВАЖЛИВО - копіюйте точно!)

#### **Authorized JavaScript origins:**
```
https://sloth-ai.lazysoft.pl
```

#### **Authorized redirect URIs:**

Видаліть всі існуючі і додайте ТІЛЬКИ ці:

```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
http://localhost:8000/api/integrations/calendar/callback/
```

⚠️ **КРИТИЧНО ВАЖЛИВО:**
- URI має закінчуватись на `/` (slash в кінці)
- Має бути `https://` (не `http://`) для production
- Має бути `/api/integrations/calendar/callback/` (не `/api/auth/google/callback/`)

### 2.4 Додайте Google Client ID та Secret в .env

```bash
nano /opt/sloth/backend/.env
```

Переконайтесь що є:
```bash
# Google OAuth (Calendar + Sheets)
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-secret
```

### 2.5 Збережіть і зачекайте

1. Натисніть **"Save"** в Google Cloud Console
2. **Зачекайте 5-10 хвилин** - Google потребує часу для застосування змін

---

## 🚀 Крок 3: Перезапустіть backend

```bash
cd /opt/sloth
docker compose -f docker-compose.prod.yml restart backend celery celery-beat
```

---

## ✅ Крок 4: Перевірте логи

```bash
# Перевірте що backend запустився без помилок
docker compose -f docker-compose.prod.yml logs backend | tail -50

# Перевірте BACKEND_URL
docker compose -f docker-compose.prod.yml exec backend python -c "from django.conf import settings; print('BACKEND_URL:', settings.BACKEND_URL)"

# Перевірте GOOGLE_CLIENT_ID
docker compose -f docker-compose.prod.yml exec backend python -c "from django.conf import settings; print('GOOGLE_CLIENT_ID:', settings.GOOGLE_CLIENT_ID[:30] if settings.GOOGLE_CLIENT_ID else 'NOT SET')"

# Перевірте FERNET_KEY
docker compose -f docker-compose.prod.yml exec backend python -c "from django.conf import settings; print('FERNET_KEY:', 'SET' if settings.FERNET_KEY else 'NOT SET')"
```

**Очікуваний результат:**
```
BACKEND_URL: https://sloth-ai.lazysoft.pl
GOOGLE_CLIENT_ID: 123456789-abcdefghijklmnopqr
FERNET_KEY: SET
```

---

## 🧪 Крок 5: Тестування

### Тест 1: Telegram Bot

1. Відкрийте: https://sloth-ai.lazysoft.pl/integrations
2. Вставте токен бота (з @BotFather)
3. Натисніть "Connect"

**✅ Очікуваний результат:** "Telegram bot connected successfully"
**❌ Якщо помилка 500:** перевірте логи `docker compose -f docker-compose.prod.yml logs backend | grep -i telegram`

### Тест 2: Google Calendar

1. Відкрийте: https://sloth-ai.lazysoft.pl/integrations
2. Натисніть "Connect Google Calendar"
3. Авторизуйтесь через Google

**✅ Очікуваний результат:** Успішне підключення
**❌ Якщо помилка 400:** перевірте URIs в Google Cloud Console (має бути точно `/api/integrations/calendar/callback/`)

---

## 🛠️ Troubleshooting

### Проблема: "redirect_uri_mismatch" все ще є

**Перевірте:**

1. **URIs в Google Cloud точно співпадають:**
   ```
   ✅ https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
   ❌ https://sloth-ai.lazysoft.pl/api/auth/google/callback/
   ❌ https://sloth-ai.lazysoft.pl/auth/google/callback/
   ```

2. **BACKEND_URL правильний:**
   ```bash
   docker compose -f docker-compose.prod.yml exec backend python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.BACKEND_URL)
   https://sloth-ai.lazysoft.pl  # Має бути БЕЗ слешу в кінці
   ```

3. **Зачекали 5-10 хвилин після збереження в Google Cloud**

4. **Очистили кеш браузера і спробували в інкогніто**

### Проблема: Telegram bot 500 error після update коду

```bash
# Перевірте логи на деталі помилки
docker compose -f docker-compose.prod.yml logs backend | grep -A 10 "Telegram"

# Перевірте FERNET_KEY
cat /opt/sloth/backend/.env | grep FERNET_KEY

# Має бути:
FERNET_KEY=pYW6EwdgPT6UnoKgzlRmYzoev34bQ0LchNOjaVBT5LM=
```

### Проблема: "GOOGLE_CLIENT_ID not set"

```bash
# Додайте в .env
nano /opt/sloth/backend/.env

# Додайте:
GOOGLE_CLIENT_ID=ваш-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-ваш-secret

# Перезапустіть
docker compose -f docker-compose.prod.yml restart backend
```

---

## 📋 Фінальний Checklist

- [ ] Оновлено код: `git pull`
- [ ] BACKEND_URL встановлено правильно в `/opt/sloth/backend/.env`
- [ ] GOOGLE_CLIENT_ID встановлено в `/opt/sloth/backend/.env`
- [ ] GOOGLE_CLIENT_SECRET встановлено в `/opt/sloth/backend/.env`
- [ ] FERNET_KEY є в `/opt/sloth/backend/.env`
- [ ] В Google Cloud додано правильні redirect URIs
- [ ] Зачекали 5-10 хвилин після збереження в Google Cloud
- [ ] Перезапущено backend: `docker compose restart backend`
- [ ] Перевірено логи: немає помилок
- [ ] Протестовано Telegram: підключається ✅
- [ ] Протестовано Google Calendar: авторизується ✅

---

## 🆘 Все ще не працює?

### Збережіть логи і надішліть:

```bash
# Backend logs
docker compose -f docker-compose.prod.yml logs backend --tail=100 > backend_logs.txt

# Перевірка змінних
docker compose -f docker-compose.prod.yml exec backend python -c "
from django.conf import settings
print('BACKEND_URL:', settings.BACKEND_URL)
print('GOOGLE_CLIENT_ID:', settings.GOOGLE_CLIENT_ID[:30] if settings.GOOGLE_CLIENT_ID else 'NOT SET')
print('FERNET_KEY:', 'SET' if settings.FERNET_KEY else 'NOT SET')
" > config_check.txt
```

Надішліть ці файли для діагностики.
