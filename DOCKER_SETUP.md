# Sloth - Швидкий запуск через Docker

## Запуск всього проекту одразу

### 1. Підготовка

Створіть `.env` файл в `backend/` директорії (скопіюйте з `.env.example`):

```bash
cp backend/.env.example backend/.env
```

Відредагуйте `backend/.env` і додайте необхідні API ключі:
- `OPENAI_API_KEY` - ваш OpenAI API ключ
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` - Google Cloud Vision API credentials
- `STRIPE_SECRET_KEY` і `STRIPE_PUBLISHABLE_KEY` - Stripe ключі
- `TWILIO_ACCOUNT_SID` і `TWILIO_AUTH_TOKEN` - Twilio credentials
- `GOOGLE_OAUTH_CLIENT_ID` і `GOOGLE_OAUTH_CLIENT_SECRET` - Google OAuth

### 2. Запуск всіх сервісів

```bash
docker-compose up --build
```

Ця команда запустить:
- ✅ PostgreSQL з pgvector (порт 5432)
- ✅ Redis (порт 6379)
- ✅ MinIO S3 storage (порти 9000, 9001)
- ✅ Django Backend API (порт 8000)
- ✅ Celery Worker (async tasks)
- ✅ Celery Beat (scheduler)
- ✅ Flower (Celery monitoring, порт 5555)
- ✅ React Frontend (порт 5173)

### 3. Доступ до сервісів

Після запуску відкрийте в браузері:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs
- **Flower (Celery)**: http://localhost:5555
- **MinIO Console**: http://localhost:9001

### 4. Створення суперкористувача

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 5. Зупинка

```bash
docker-compose down
```

Або з видаленням volumes (БД буде очищено):

```bash
docker-compose down -v
```

## Корисні команди

### Перегляд логів

```bash
# Всі сервіси
docker-compose logs -f

# Тільки backend
docker-compose logs -f backend

# Тільки celery
docker-compose logs -f celery
```

### Виконання команд в контейнері

```bash
# Django migrations
docker-compose exec backend python manage.py migrate

# Django shell
docker-compose exec backend python manage.py shell

# Celery inspect
docker-compose exec celery celery -A config inspect active
```

### Rebuild без кешу

```bash
docker-compose build --no-cache
docker-compose up
```

## Архітектура

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                    │
│                   localhost:5173                        │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend (Django REST)                  │
│                   localhost:8000                        │
└─────────────────────────────────────────────────────────┘
         │               │                │
         ▼               ▼                ▼
  ┌──────────┐   ┌────────────┐   ┌──────────────┐
  │PostgreSQL│   │   Redis    │   │    MinIO     │
  │ +pgvector│   │            │   │  (S3 API)    │
  └──────────┘   └────────────┘   └──────────────┘
         │               │
         ▼               ▼
  ┌──────────────────────────────┐
  │  Celery Worker + Beat        │
  │  (Async Tasks & Scheduler)   │
  └──────────────────────────────┘
```

## Troubleshooting

### PostgreSQL не запускається
```bash
docker-compose down -v
docker volume prune
docker-compose up --build
```

### Backend не може підключитися до БД
Перевірте що postgres сервіс healthy:
```bash
docker-compose ps
```

### Frontend не бачить Backend
Перевірте що в `vite.config.js` правильно налаштований proxy або CORS в Django.

### Celery tasks не виконуються
Перевірте логи:
```bash
docker-compose logs -f celery
docker-compose logs -f redis
```
