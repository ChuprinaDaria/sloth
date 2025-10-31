# Google Calendar Integration - AI-Powered Booking

## 🎯 Функціонал

1. ✅ **OAuth2 авторизація** - повний flow з Google
2. ✅ **Перевірка вільних слотів** - автоматично дивиться зайнятість
3. ✅ **AI-асистент бронювання** - розуміє контекст розмови
4. ✅ **Google Meet посилання** - автоматично створюються
5. ✅ **Email підтвердження** - красивий HTML шаблон
6. ✅ **Природня мова** - "tomorrow", "next monday", "завтра"

---

## 🚀 Як це працює

### 1. Підключення Calendar (OAuth2 Flow)

```javascript
// Frontend кликає "Connect Google Calendar"
GET /api/integrations/calendar/auth/

// Response:
{
  "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
  "state": "random_state"
}

// Frontend перенаправляє user на authorization_url
window.location.href = authorization_url;

// Користувач авторизується в Google → Google redirect назад:
GET /api/integrations/calendar/callback/?code=AUTH_CODE&state=...

// Backend:
1. Обмінює code на access_token & refresh_token
2. Зберігає Integration з encrypted tokens
3. Redirect на frontend: /integrations?success=calendar_connected
```

**Важливо:** Токени зберігаються зашифровані через Fernet!

### 2. AI Асистент розуміє розмову

```
User: "Хочу записатися на стрижку завтра"

AI Agent:
1. Розпізнає Intent: booking appointment
2. Витягує інформацію:
   - Сервіс: "стрижку" → Haircut
   - Дата: "завтра" → tomorrow
3. Викликає check_calendar_availability("tomorrow", 60)
4. Отримує вільні слоти: "9:00 AM, 11:00 AM, 2:00 PM, 4:00 PM"
5. Відповідає: "На завтра вільно о 9:00, 11:00, 14:00 та 16:00. Який час вам підходить?"

User: "14:00 підходить. John Doe, john@example.com"

AI Agent:
1. Розпізнає підтвердження
2. Витягує дані:
   - Name: John Doe
   - Email: john@example.com
   - Time: 14:00
3. Викликає book_appointment(
      customer_name="John Doe",
      customer_email="john@example.com",
      service="Haircut",
      date="tomorrow",
      time="14:00"
   )
4. Створюється:
   ✅ Google Calendar event
   ✅ Google Meet link
   ✅ Email підтвердження відправлено
5. Відповідає: "Готово! Записав вас на стрижку завтра о 14:00. Google Meet посилання і підтвердження відправлені на john@example.com"
```

---

## 🧠 AI Function Calling

AI Agent має доступ до 2 функцій:

### 1. `check_calendar_availability`

```python
{
  "name": "check_calendar_availability",
  "description": "Check available time slots in the calendar",
  "parameters": {
    "date": "tomorrow",        # or "next monday", "2024-11-15"
    "duration_minutes": 60      # appointment length
  }
}
```

**Повертає:**
```
"Available times: 9:00 AM, 11:00 AM, 2:00 PM, 4:00 PM"
```

### 2. `book_appointment`

```python
{
  "name": "book_appointment",
  "description": "Book an appointment in the calendar",
  "parameters": {
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "service": "Haircut",
    "date": "tomorrow",
    "time": "14:00",
    "duration_minutes": 60,
    "create_meet": true
  }
}
```

**Повертає:**
```
✅ Appointment booked successfully!

📅 Haircut for John Doe
🕐 Tuesday, November 05 at 02:00 PM
⏱️ Duration: 60 minutes
🎥 Google Meet: https://meet.google.com/abc-defg-hij
📧 Confirmation email sent to john@example.com
```

---

## 📧 Email Confirmation

Клієнт автоматично отримує email з:

- ✅ Деталями запису (дата, час, сервіс)
- ✅ Google Meet посиланням (якщо створено)
- ✅ Кнопкою "Add to Calendar"
- ✅ Нагадуванням за 24 години

**Приклад HTML:**

```html
<h2>Appointment Confirmed! ✅</h2>

<div>
  <h3>Appointment Details:</h3>
  <p><strong>Service:</strong> Haircut</p>
  <p><strong>Date:</strong> Tuesday, November 05, 2024</p>
  <p><strong>Time:</strong> 02:00 PM</p>
  <p><strong>Duration:</strong> 60 minutes</p>
</div>

<div>
  <h3>🎥 Video Consultation</h3>
  <a href="https://meet.google.com/...">Join Meeting</a>
</div>
```

---

## 🔄 Як це працює під капотом

### Схема взаємодії:

```
1. User → Chat: "Хочу записатися на завтра"
         ↓
2. AI Agent → Аналізує повідомлення
         ↓
3. Детектує ключові слова: ["запис", "бронь", "appointment"]
         ↓
4. Додає до context: "Calendar Integration Available"
         ↓
5. OpenAI GPT-4 з function calling:
   {
     "tool_calls": [{
       "function": "check_calendar_availability",
       "arguments": {"date": "tomorrow", "duration_minutes": 60}
     }]
   }
         ↓
6. Backend виконує: calendar_tools.check_availability("tomorrow", 60)
         ↓
7. GoogleCalendarService:
   - Запитує freebusy для tomorrow
   - Фільтрує зайняті slots
   - Повертає вільні: ["9:00 AM", "11:00 AM", "2:00 PM"]
         ↓
8. OpenAI отримує результат → генерує відповідь:
   "На завтра вільно о 9:00, 11:00 та 14:00"
         ↓
9. User → "14:00, John Doe, john@example.com"
         ↓
10. AI → book_appointment(...)
         ↓
11. GoogleCalendarService.create_appointment:
    - Створює event в Google Calendar
    - Додає conferenceData для Google Meet
    - Додає attendee (john@example.com)
    - Google автоматично відправляє календарне запрошення
         ↓
12. BookingEmailService.send_confirmation:
    - Формує красивий HTML email
    - Відправляє через Django mail
         ↓
13. AI → "Готово! Записав вас..."
```

---

## 🛠️ API Endpoints

### Підключення

```bash
# 1. Отримати authorization URL
GET /api/integrations/calendar/auth/
Authorization: Bearer JWT_TOKEN

Response:
{
  "authorization_url": "https://accounts.google.com/...",
  "state": "..."
}

# 2. Redirect user → Google OAuth
# 3. Google redirects back
GET /api/integrations/calendar/callback/?code=...&state=...

# Auto-redirects to frontend with success/error
```

### Перевірка слотів (опціонально, можна через AI)

```bash
GET /api/integrations/calendar/slots/?date=tomorrow&duration=60
Authorization: Bearer JWT_TOKEN

Response:
{
  "slots": "Available times: 9:00 AM, 11:00 AM, 2:00 PM"
}
```

### Чат з AI (автоматично використовує calendar)

```bash
POST /api/agent/chat/
{
  "message": "Хочу записатися на завтра о 14:00"
}

# AI автоматично:
# 1. Перевіряє доступність
# 2. Бронює якщо всі дані є
# 3. Відправляє email
```

---

## 🧩 Природня мова (NLP)

AI розуміє:

### Дати:
- `today`, `сьогодні` → сьогодні
- `tomorrow`, `завтра` → завтра
- `day after tomorrow`, `післязавтра`
- `next monday`, `next week`
- `2024-11-15`, `15/11/2024`

### Час:
- `14:00`, `2:00 PM`, `2pm`
- `10am`, `10:30`

### Контекст з розмови:
```
User: "Хочу на маникюр"
AI: "На який день?"
User: "Завтра"
AI: (knows service=Manicure, date=tomorrow)
```

---

## 📊 База даних

### Integration Model:

```python
Integration(
    user_id=1,
    integration_type='google_calendar',
    status='active',
    credentials_encrypted=Fernet(SECRET_KEY).encrypt({
        'access_token': '...',
        'refresh_token': '...',
        'token_expiry': '2024-12-31T...'
    }),
    settings={
        'timezone': 'Europe/Kiev'
    }
)
```

### Message Model (зберігає історію з function calls):

```python
Message(
    conversation=conversation,
    role='assistant',
    content='Записав вас на завтра о 14:00...',
    metadata={
        'function_calls': [
            {
                'function': 'book_appointment',
                'arguments': {
                    'customer_name': 'John Doe',
                    'service': 'Haircut',
                    'date': 'tomorrow',
                    'time': '14:00'
                },
                'result': 'success'
            }
        ]
    }
)
```

---

## ⚙️ Налаштування

### 1. Google Cloud Console

```bash
1. Create Project
2. Enable APIs:
   - Google Calendar API
   - Google Meet API (optional)
3. Create OAuth 2.0 credentials:
   - Type: Web application
   - Authorized redirect URIs:
     https://yourapi.com/api/integrations/calendar/callback/
4. Copy Client ID and Client Secret
```

### 2. Django Settings

```python
# .env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
BACKEND_URL=https://yourapi.com
```

### 3. Scopes

```python
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
]
```

---

## 🎓 Приклади використання

### Простий запис:

```
User: "Хочу записатися на завтра"
AI: "На який час?"
User: "14:00"
AI: "На яку послугу?"
User: "Стрижка. John Doe, john@example.com"
AI: ✅ Записав!
```

### Складний запис:

```
User: "Запишіть Марію Коваленко (maria@example.com) на маникюр на наступний понеділок о 10:00"
AI: (автоматично все розпарсить і забукає) ✅ Готово!
```

### Перевірка доступності:

```
User: "Які вільні слоти на вівторок?"
AI: "На вівторок вільно: 9:00, 11:00, 13:00, 15:00, 17:00"
User: "15:00 підходить"
AI: "Чудово! Як вас звати та ваш email?"
```

---

## 🔒 Безпека

- ✅ OAuth2 з CSRF protection (state parameter)
- ✅ Tokens зашифровані (Fernet + SECRET_KEY)
- ✅ Refresh tokens для довгострокового доступу
- ✅ Scopes обмежені тільки календарем
- ✅ Email validation перед bookingом

---

## 🐛 Troubleshooting

### OAuth fails

```bash
# Check redirect URI matches exactly
BACKEND_URL=https://yourapi.com  # NO trailing slash!
```

### Calendar not showing

```python
# Check if integration exists and active
Integration.objects.filter(
    user_id=user.id,
    integration_type='google_calendar',
    status='active'
)
```

### Tokens expired

```python
# Google refresh_token automatically refreshes
# If fails → user needs to re-authorize
```

---

Готово! Тепер AI асистент може **самостійно** бронювати клієнтів 🎉
