# 🔐 Google OAuth Setup Guide

## ❌ Проблема: "Error 400: redirect_uri_mismatch"

Ця помилка означає, що `redirect_uri` в вашому запиті не співпадає з тим, який налаштований в Google Cloud Console.

## ✅ Рішення: Налаштуйте правильний Redirect URI

### Крок 1: Визначте ваш BACKEND_URL

Для production сервера `sloth-ai.lazysoft.pl`, ваші redirect URIs повинні бути:

```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
https://sloth-ai.lazysoft.pl/api/integrations/instagram/callback/
```

⚠️ **ВАЖЛИВО**: URI має **ТОЧНО** співпадати, включно з:
- Протоколом (https://)
- Доменом
- Слешем в кінці `/`

---

## 📋 Покрокова інструкція

### 1️⃣ Відкрийте Google Cloud Console

1. Перейдіть на [Google Cloud Console](https://console.cloud.google.com/)
2. Виберіть ваш проект (або створіть новий)

### 2️⃣ Налаштуйте OAuth 2.0

1. В меню зліва виберіть **APIs & Services** → **Credentials**
2. Знайдіть ваш **OAuth 2.0 Client ID** (або створіть новий)
3. Натисніть на назву Client ID для редагування

### 3️⃣ Додайте Authorized Redirect URIs

В розділі **Authorized redirect URIs** додайте:

#### 🌐 Production (sloth-ai.lazysoft.pl):
```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
https://sloth-ai.lazysoft.pl/api/integrations/instagram/callback/
```

#### 💻 Development (localhost):
```
http://localhost:8000/api/integrations/calendar/callback/
http://localhost:8000/api/integrations/instagram/callback/
```

### 4️⃣ Натисніть "Save"

Зачекайте 5-10 хвилин, поки зміни застосуються.

---

## 🔍 Перевірка налаштувань

### На сервері перевірте BACKEND_URL:

```bash
cat /opt/sloth/backend/.env | grep BACKEND_URL
```

**Має бути:**
```
BACKEND_URL=https://sloth-ai.lazysoft.pl
```

⚠️ **БЕЗ слешу в кінці!**

### Перевірте що змінні встановлені:

```bash
cat /opt/sloth/backend/.env | grep GOOGLE
```

**Має показати:**
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret
```

---

## 🚀 Тестування

### 1. Перезапустіть backend:

```bash
cd /opt/sloth
docker compose -f docker-compose.prod.yml restart backend
```

### 2. Перевірте логи:

```bash
docker compose -f docker-compose.prod.yml logs -f backend | grep -i oauth
```

### 3. Спробуйте підключити Google Calendar:

1. Відкрийте https://sloth-ai.lazysoft.pl/integrations
2. Натисніть "Connect Google Calendar"
3. Авторизуйтеся через Google

Якщо все правильно - ви побачите успішне підключення!

---

## 🛠️ Troubleshooting

### Помилка: "redirect_uri_mismatch" все ще з'являється

**Перевірте:**

1. **URI точно співпадають** (включно з регістром)
   - ✅ `https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/`
   - ❌ `https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback` (без слешу)
   - ❌ `http://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/` (http замість https)

2. **BACKEND_URL в .env правильний:**
   ```bash
   # Перевірте
   docker compose -f docker-compose.prod.yml exec backend python -c "from django.conf import settings; print('BACKEND_URL:', settings.BACKEND_URL)"
   ```

3. **Google OAuth credentials правильні:**
   ```bash
   # Перевірте CLIENT_ID
   docker compose -f docker-compose.prod.yml exec backend python -c "from django.conf import settings; print('CLIENT_ID:', settings.GOOGLE_CLIENT_ID[:20])"
   ```

4. **Зачекайте 5-10 хвилин** після збереження в Google Cloud Console

### Помилка: "OAuth not configured"

Це означає що GOOGLE_CLIENT_ID або GOOGLE_CLIENT_SECRET не встановлені.

**Виправлення:**

```bash
nano /opt/sloth/backend/.env
```

Додайте:
```bash
# Google OAuth (Calendar + Sheets)
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-secret-here
```

Перезапустіть:
```bash
docker compose -f docker-compose.prod.yml restart backend celery celery-beat
```

---

## 📦 Які API потрібно увімкнути в Google Cloud?

1. **Google Calendar API**
2. **Google Sheets API** (для Sheets integration)
3. **Google People API** (опціонально, для профілів)

### Як увімкнути:

1. Google Cloud Console → **APIs & Services** → **Library**
2. Знайдіть потрібний API
3. Натисніть **Enable**

---

## 🔐 OAuth Consent Screen

Не забудьте налаштувати OAuth Consent Screen:

1. Google Cloud Console → **APIs & Services** → **OAuth consent screen**
2. Виберіть **External** (для публічного доступу)
3. Заповніть обов'язкові поля:
   - App name: **Sloth AI**
   - User support email: ваш email
   - Developer contact: ваш email
4. **Scopes**: Додайте необхідні scope
   - `https://www.googleapis.com/auth/calendar`
   - `https://www.googleapis.com/auth/calendar.events`
   - `https://www.googleapis.com/auth/spreadsheets`

5. **Test users** (якщо app в Testing mode): Додайте email адреси користувачів

---

## ✅ Checklist

- [ ] Створено OAuth 2.0 Client ID в Google Cloud Console
- [ ] Додано redirect URIs для production та development
- [ ] Увімкнено Google Calendar API та Google Sheets API
- [ ] Налаштовано OAuth Consent Screen
- [ ] Встановлено GOOGLE_CLIENT_ID в backend/.env
- [ ] Встановлено GOOGLE_CLIENT_SECRET в backend/.env
- [ ] Встановлено BACKEND_URL=https://sloth-ai.lazysoft.pl в backend/.env
- [ ] Перезапущено backend сервіс
- [ ] Протестовано підключення Google Calendar

---

## 📞 Підтримка

Якщо проблема залишається:

1. Перевірте логи backend:
   ```bash
   docker compose -f docker-compose.prod.yml logs backend | tail -100
   ```

2. Перевірте network запити в браузері (Developer Tools → Network)

3. Переконайтесь що BACKEND_URL доступний з інтернету:
   ```bash
   curl https://sloth-ai.lazysoft.pl/health/
   ```
