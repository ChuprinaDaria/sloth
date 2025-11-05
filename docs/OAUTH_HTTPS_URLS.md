# OAuth Callback URLs для HTTPS

## Огляд

Після налаштування SSL сертифікатів для `sloth-ai.lazysoft.pl`, необхідно **оновити OAuth callback URLs** у всіх OAuth провайдерах на HTTPS версії.

## ✅ Список OAuth Providers

### 1. Google OAuth (Calendar + Sheets)

**Console**: [Google Cloud Console](https://console.cloud.google.com/)

**Кроки**:
1. Виберіть ваш проєкт Sloth AI
2. Перейдіть до **APIs & Services** → **Credentials**
3. Оберіть OAuth 2.0 Client ID
4. Додайте до **Authorized redirect URIs**:

```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
```

**Важливо**:
- ✅ Використовуйте `https://` (не `http://`)
- ✅ Завершуйте URL слешем `/`
- ✅ Перевірте що немає зайвих пробілів

---

### 2. Facebook/Instagram API

**Console**: [Facebook Developers](https://developers.facebook.com/)

**Кроки**:

#### A. Basic Settings
1. Виберіть ваш додаток Sloth AI
2. Перейдіть до **Settings** → **Basic**
3. Додайте до **App Domains**:
```
sloth-ai.lazysoft.pl
```

#### B. Facebook Login Settings
1. У лівому меню виберіть **Products** → **Facebook Login** → **Settings**
2. Додайте до **Valid OAuth Redirect URIs**:
```
https://sloth-ai.lazysoft.pl/api/integrations/instagram/callback/
```

#### C. Webhooks
1. У лівому меню виберіть **Products** → **Webhooks**
2. Оберіть **Instagram** або **Page**
3. Встановіть **Callback URL**:
```
https://sloth-ai.lazysoft.pl/api/integrations/webhooks/instagram/
```

4. **Verify Token** (із вашого `.env` файлу):
```
FACEBOOK_WEBHOOK_VERIFY_TOKEN=sloth_instagram_webhook_2024
```

5. Підпишіться на події:
   - ✅ `messages`
   - ✅ `messaging_postbacks`
   - ✅ `message_deliveries`
   - ✅ `message_reads`

---

### 3. Stripe Webhooks

**Dashboard**: [Stripe Dashboard](https://dashboard.stripe.com/)

**Кроки**:
1. Перейдіть до **Developers** → **Webhooks**
2. Якщо є старий endpoint, **видаліть** його
3. Натисніть **Add endpoint**
4. Встановіть **Endpoint URL**:
```
https://sloth-ai.lazysoft.pl/webhooks/stripe/
```

5. Виберіть події для прослуховування:
   - ✅ `payment_intent.succeeded`
   - ✅ `payment_intent.payment_failed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`

6. Скопіюйте **Signing secret** і додайте до `.env`:
```env
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

### 4. Telegram Bot Webhook

**API**: Telegram Bot API

Оновіть webhook через команду `curl`:

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://sloth-ai.lazysoft.pl/api/integrations/webhooks/telegram/<YOUR_BOT_TOKEN>/",
    "allowed_updates": ["message", "callback_query"]
  }'
```

**Замініть**:
- `<YOUR_BOT_TOKEN>` - ваш Telegram bot token

**Перевірка webhook**:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

Має показати:
```json
{
  "ok": true,
  "result": {
    "url": "https://sloth-ai.lazysoft.pl/api/integrations/webhooks/telegram/YOUR_TOKEN/",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

### 5. Twilio (WhatsApp)

**Console**: [Twilio Console](https://www.twilio.com/console)

**Кроки**:
1. Перейдіть до **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
   (або ваш production WhatsApp номер)
2. Знайдіть секцію **Sandbox Configuration**
3. Встановіть **When a message comes in**:
```
https://sloth-ai.lazysoft.pl/api/integrations/webhooks/whatsapp/
```

4. HTTP Method: **POST**

---

## Перелік Усіх URLs

### OAuth Callbacks
```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
https://sloth-ai.lazysoft.pl/api/integrations/instagram/callback/
```

### Webhooks
```
https://sloth-ai.lazysoft.pl/api/integrations/webhooks/telegram/<BOT_TOKEN>/
https://sloth-ai.lazysoft.pl/api/integrations/webhooks/whatsapp/
https://sloth-ai.lazysoft.pl/api/integrations/webhooks/instagram/
https://sloth-ai.lazysoft.pl/webhooks/stripe/
```

---

## Тестування OAuth Flow

### 1. Google Calendar

```bash
# Отримайте auth URL через API
curl -X GET "https://sloth-ai.lazysoft.pl/api/integrations/calendar/auth/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Відкрийте URL у браузері
# Після авторизації має перенаправити назад на callback
```

**Очікуваний результат**: Redirect на `https://sloth-ai.lazysoft.pl/integrations?success=calendar_connected`

### 2. Instagram

```bash
# Отримайте auth URL
curl -X GET "https://sloth-ai.lazysoft.pl/api/integrations/instagram/auth/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Відкрийте URL у браузері
```

**Очікуваний результат**: Redirect на `https://sloth-ai.lazysoft.pl/integrations?success=instagram_connected&username=YOUR_IG`

### 3. Telegram Webhook

```bash
# Надішліть тестове повідомлення боту
# Перевірте логи Django
docker-compose logs -f backend | grep -i telegram
```

**Очікуваний результат**: Лог `Telegram webhook received for bot_token=...`

---

## Поширені Помилки

### ❌ Error: `redirect_uri_mismatch`

**Причина**: URL у OAuth провайдері не співпадає з URL у коді

**Рішення**:
1. Перевірте що у провайдері вказано **точний** URL з `https://`
2. Перевірте наявність/відсутність trailing slash `/`
3. Перевірте що домен співпадає: `sloth-ai.lazysoft.pl`

### ❌ Error: `invalid_state`

**Причина**: CSRF токен не співпадає (можливо застарілий)

**Рішення**:
1. Очистіть cookies браузера
2. Спробуйте знову отримати auth URL
3. Не використовуйте старі auth URLs

### ❌ Error: `callback_failed`

**Причина**: Помилка на бекенді під час обробки callback

**Рішення**:
1. Перевірте логи Django:
```bash
docker-compose logs -f backend
```

2. Перевірте що `BACKEND_URL` налаштований правильно:
```bash
docker-compose exec backend env | grep BACKEND_URL
# Має бути: BACKEND_URL=https://sloth-ai.lazysoft.pl
```

### ❌ Webhook не працює

**Симптоми**: Повідомлення не приходять

**Рішення**:
1. Перевірте що webhook URL використовує `https://`
2. Перевірте що SSL сертифікат валідний:
```bash
curl -I https://sloth-ai.lazysoft.pl
# Має бути HTTP/2 200
```

3. Перевірте логи webhook:
```bash
docker-compose logs -f backend | grep -i webhook
```

4. Для Telegram, перевірте webhook info:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

---

## Environment Variables Checklist

Переконайтеся що у production `.env` файлі:

```bash
# URLs
BACKEND_URL=https://sloth-ai.lazysoft.pl
FRONTEND_URL=https://sloth-ai.lazysoft.pl

# Domains
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl,www.lazysoft.pl
CORS_ALLOWED_ORIGINS=https://sloth-ai.lazysoft.pl

# Security (для HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# OAuth Credentials
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
FACEBOOK_APP_ID=your-app-id
FACEBOOK_APP_SECRET=your-app-secret
FACEBOOK_WEBHOOK_VERIFY_TOKEN=sloth_instagram_webhook_2024

# Webhooks
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Швидка Перевірка (Checklist)

Перед тим як тестувати, переконайтеся:

- [ ] SSL сертифікати встановлені (`/etc/letsencrypt/live/sloth-ai.lazysoft.pl/`)
- [ ] Nginx налаштований і працює (`sudo systemctl status nginx`)
- [ ] `.env` файл містить `BACKEND_URL=https://sloth-ai.lazysoft.pl`
- [ ] Docker контейнери перезапущені з новими environment variables
- [ ] Google OAuth callback URL оновлений на HTTPS
- [ ] Facebook/Instagram OAuth callback URL оновлений на HTTPS
- [ ] Instagram webhook URL оновлений на HTTPS
- [ ] Stripe webhook endpoint оновлений на HTTPS
- [ ] Telegram webhook встановлений на HTTPS URL
- [ ] Twilio/WhatsApp webhook оновлений на HTTPS

---

## Автоматизація (Опціонально)

Для автоматичного оновлення Telegram webhook при зміні URL:

```python
# backend/apps/integrations/management/commands/update_telegram_webhooks.py
from django.core.management.base import BaseCommand
from apps.integrations.models import Integration
from apps.integrations.telegram_manager import update_webhook_url
import asyncio

class Command(BaseCommand):
    help = 'Update Telegram webhooks for all active bots'

    def handle(self, *args, **options):
        integrations = Integration.objects.filter(
            integration_type='telegram',
            is_active=True
        )

        for integration in integrations:
            self.stdout.write(f"Updating webhook for bot {integration.id}...")
            loop = asyncio.new_event_loop()
            success = loop.run_until_complete(update_webhook_url(integration))
            loop.close()

            if success:
                self.stdout.write(self.style.SUCCESS(f'✓ Bot {integration.id} updated'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ Bot {integration.id} failed'))
```

Запуск:
```bash
docker-compose exec backend python manage.py update_telegram_webhooks
```

---

**Посилання**:
- [SSL Setup Guide](./SSL_SETUP.md)
- [Quick Start Commands](./SSL_QUICK_START.md)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Facebook OAuth Documentation](https://developers.facebook.com/docs/facebook-login)
- [Stripe Webhooks Guide](https://stripe.com/docs/webhooks)
- [Telegram Bot API Webhooks](https://core.telegram.org/bots/api#setwebhook)
