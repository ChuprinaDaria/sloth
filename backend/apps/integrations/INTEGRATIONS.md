# Інтеграції - Як це працює

## 🎯 Загальна концепція

Кожен користувач може підключити свого Telegram бота, WhatsApp номер, або Google Calendar.
**Важливо:** Кожен користувач має **свого окремого бота**, який працює **тільки для нього**.

---

## 📱 Telegram Bot

### Як працює

1. **Користувач створює бота** через @BotFather в Telegram
2. **Отримує bot_token** (наприклад: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
3. **Додає токен в інтерфейсі** Sloth
4. **Backend автоматично**:
   - Зберігає Integration запис у БД
   - Запускає `TelegramBotManager` який реєструє бота
   - Налаштовує webhook: `https://yourapi.com/webhooks/telegram/{bot_token}/`
   - Telegram починає відправляти всі повідомлення на цей endpoint

### Архітектура: Webhook Mode

```
┌────────────────────────────────────────────────────────────┐
│  User 1: Bot Token ABC123                                  │
│  User 2: Bot Token DEF456                                  │
│  User 3: Bot Token GHI789                                  │
└────────────────────────────────────────────────────────────┘
                        ↓
         Telegram відправляє повідомлення
                        ↓
┌────────────────────────────────────────────────────────────┐
│  Django Backend (один endpoint на всіх)                    │
│  /api/integrations/webhooks/telegram/{bot_token}/          │
└────────────────────────────────────────────────────────────┘
                        ↓
        TelegramBotManager дивиться bot_token
                        ↓
        Знаходить Integration за токеном
                        ↓
        Визначає якому користувачу належить
                        ↓
        Обробляє повідомлення через AI Agent
                        ↓
        Відправляє відповідь назад в Telegram
```

### Що відбувається при підключенні

```python
# Frontend відправляє
POST /api/integrations/telegram/connect/
{
    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
}

# Backend:
1. Створює Integration запис:
   Integration(
       user_id=current_user.id,
       integration_type='telegram',
       credentials_encrypted=encrypt(bot_token),
       status='pending'
   )

2. Запускає start_telegram_bot(integration):
   - Створює Application (python-telegram-bot)
   - Додає handlers (message, commands)
   - Налаштовує webhook в Telegram API:
     bot.set_webhook(url=f"{BACKEND_URL}/webhooks/telegram/{bot_token}/")

3. Зберігає бота в TelegramBotManager._bots:
   {
       integration_id: {
           'app': Application,
           'bot_token': bot_token,
           'integration_id': integration.id
       }
   }

4. Змінює статус на 'active'
```

### Обробка повідомлення

```python
# Telegram відправляє webhook:
POST /api/integrations/webhooks/telegram/123456789:ABC.../
{
    "update_id": 123,
    "message": {
        "chat": {"id": 987654321},
        "text": "Привіт! Хочу записатися на стрижку"
    }
}

# Backend:
1. TelegramWebhookView отримує bot_token з URL
2. Викликає process_telegram_webhook(bot_token, update_data)
3. TelegramBotManager:
   - Знаходить Integration за bot_token
   - Визначає user_id
   - Отримує tenant schema
   - Створює/знаходить Conversation
4. AgentService:
   - Обробляє повідомлення через AI
   - Шукає контекст в RAG (документи, фото)
   - Генерує відповідь через OpenAI
5. Відправляє відповідь назад:
   bot.send_message(chat_id, response)
```

### Автоматичний перезапуск

При рестарті сервера:

```python
# В apps.integrations.apps.IntegrationsConfig.ready():
start_all_active_telegram_bots.delay()

# Celery task знаходить всі active Integration типу 'telegram'
# І запускає їх знову
```

### Переваги Webhook Mode

✅ **Масштабованість** - один процес обробляє тисячі ботів
✅ **Економія ресурсів** - не потрібен окремий процес на кожного бота
✅ **Швидкість** - Telegram одразу доставляє повідомлення
✅ **Production-ready** - рекомендований підхід Telegram

---

## 💬 WhatsApp (Twilio)

### Як працює

WhatsApp працює простіше, бо **Twilio сам є посередником**:

```
User's phone number +380123456789
      ↓ WhatsApp message
Twilio WhatsApp Business number +14155238886
      ↓ HTTP webhook
Django Backend /api/integrations/webhooks/whatsapp/
      ↓ Знаходить Integration за Twilio number
AI Agent processes message
      ↓ Response via Twilio API
Twilio sends WhatsApp message
      ↓
User receives response
```

### Підключення

```python
# User надає:
{
    "account_sid": "ACxxxxx",
    "auth_token": "xxxxx",
    "whatsapp_number": "+14155238886"  # Twilio number
}

# Backend:
1. Зберігає Integration з encrypted credentials
2. Показує webhook URL:
   https://yourapi.com/api/integrations/webhooks/whatsapp/

3. Користувач ВРУЧНУ налаштовує цей webhook в Twilio Console
```

### Обробка вхідного повідомлення

```python
# Twilio відправляє POST (form-encoded):
{
    "From": "whatsapp:+380123456789",  # Customer
    "To": "whatsapp:+14155238886",     # Your Twilio number
    "Body": "Hello, I want to book..."
}

# Backend:
1. Знаходить Integration за номером "To"
2. Визначає user_id власника цього номера
3. Обробляє через AI Agent
4. Відправляє відповідь через Twilio API
```

---

## 📅 Google Calendar

### OAuth2 Flow

1. Frontend перенаправляє на Google OAuth
2. Користувач дає дозволи
3. Frontend отримує `access_token` та `refresh_token`
4. Backend зберігає токени encrypted
5. Може читати/створювати події в календарі

```python
# Приклад використання
calendar_service = GoogleCalendarService(integration)
events = calendar_service.list_events(max_results=10)
```

---

## 🔐 Безпека

### Шифрування Credentials

Всі токени та паролі шифруються перед збереженням:

```python
# In Integration.set_credentials():
credentials_dict = {'bot_token': '123:ABC'}
encrypted = Fernet(SECRET_KEY).encrypt(json.dumps(credentials_dict))
integration.credentials_encrypted = encrypted

# In Integration.get_credentials():
decrypted = Fernet(SECRET_KEY).decrypt(integration.credentials_encrypted)
return json.loads(decrypted)
```

### Webhook Security

- ✅ Bot token в URL (Telegram) - ідентифікує бота
- ✅ Twilio validates signatures (можна додати)
- ✅ CSRF exempt тільки для webhook endpoints
- ✅ Всі дані ізольовані по tenant schemas

---

## 🚀 Deployment

### Змінні оточення

```bash
# .env
BACKEND_URL=https://api.yourdomain.com
TELEGRAM_BOT_TOKEN=  # optional, fallback
TWILIO_ACCOUNT_SID=  # optional, fallback
TWILIO_AUTH_TOKEN=   # optional, fallback
```

### Celery Tasks

Додайте в `config/celery.py`:

```python
app.conf.beat_schedule = {
    'start-telegram-bots': {
        'task': 'apps.integrations.tasks.start_all_active_telegram_bots',
        'schedule': crontab(minute='*/30'),  # Every 30 min
    },
    'check-integration-health': {
        'task': 'apps.integrations.tasks.check_integration_health',
        'schedule': crontab(minute='0', hour='*/1'),  # Every hour
    },
}
```

---

## 📊 Моніторинг

### Перевірка статусу

```sql
SELECT
    u.email,
    i.integration_type,
    i.status,
    i.messages_received,
    i.messages_sent,
    i.last_activity
FROM integrations i
JOIN users u ON u.id = i.user_id
WHERE i.status = 'active';
```

### Logs

```bash
# Telegram
docker-compose logs -f backend | grep "Telegram"

# Webhook requests
docker-compose logs -f backend | grep "webhook"
```

---

## ❓ Troubleshooting

### Telegram бот не відповідає

```python
# 1. Перевірте чи бот зареєстрований
from apps.integrations.telegram_manager import telegram_bot_manager
print(telegram_bot_manager._bots)

# 2. Перевірте webhook в Telegram
import telegram
bot = telegram.Bot(token='YOUR_TOKEN')
info = bot.get_webhook_info()
print(info)

# 3. Перезапустіть бота
integration = Integration.objects.get(id=1)
await stop_telegram_bot(integration.id)
await start_telegram_bot(integration)
```

### WhatsApp не працює

1. Перевірте чи webhook налаштований в Twilio Console
2. Перевірте чи Twilio number активний
3. Подивіться логи в Twilio Console → Debugger

### Бот зупинився після перезапуску сервера

Це нормально - Django автоматично запустить через `apps.py.ready()`.
Якщо не запустився - перевірте Celery worker.

---

## 🎓 Best Practices

1. **Завжди шифруйте credentials**
2. **Використовуйте webhook mode** (не long polling)
3. **Обробляйте помилки gracefully**
4. **Логуйте всі webhook requests**
5. **Rate limit webhooks** (захист від спаму)
6. **Моніторте активність** через Celery tasks
7. **Тестуйте на локальному ngrok** перед production

---

Готово! Тепер ви знаєте як працюють інтеграції 🎉
