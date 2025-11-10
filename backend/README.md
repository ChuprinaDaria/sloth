# Sloth AI Agent - Backend

Django REST API бекенд для платформи автоматизації салонів краси через AI агента.

## Технологічний стек

- **Django 5.0** + **Django REST Framework** - REST API
- **PostgreSQL 16** + **pgvector** - база даних з векторним пошуком
- **Celery** + **Redis** - асинхронна обробка задач
- **OpenAI API** - AI агент та векторизація
- **Google Cloud Vision** - розпізнавання зображень
- **Stripe** - обробка платежів
- **Docker** + **Docker Compose** - контейнеризація

## Архітектура

### Multi-tenant (Мультитенантність)

Кожен клієнт має окрему PostgreSQL schema для повної ізоляції даних:

```
public schema:
  - users
  - organizations
  - subscriptions
  - plans

tenant_xxx schema (для кожного клієнта):
  - profiles
  - documents
  - photos
  - embeddings
  - conversations
  - messages
  - integrations
```

### Додатки (Apps)

1. **accounts** - Користувачі, організації, автентифікація
2. **subscriptions** - Підписки, плани, Stripe інтеграція
3. **referrals** - Реферальна система (50 активних юзерів = апгрейд)
4. **documents** - Завантаження та обробка документів (PDF, DOCX, Excel)
5. **embeddings** - Векторизація тексту (RAG)
6. **agent** - AI агент (чат з RAG контекстом)
7. **integrations** - Telegram, WhatsApp, Google Calendar

## Швидкий старт

### 1. Клонування репозиторію

```bash
cd backend
```

### 2. Налаштування змінних оточення

```bash
cp .env.example .env
```

Відредагуйте `.env` та додайте ваші API ключі:

```env
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
STRIPE_SECRET_KEY=your-stripe-key
# ... інші змінні
```

### 3. Запуск через Docker Compose

```bash
docker-compose up -d
```

Це запустить:
- PostgreSQL (порт 5432)
- Redis (порт 6379)
- Django backend (порт 8000)
- Celery worker
- Celery beat (scheduler)
- Flower (Celery monitoring, порт 5555)
- MinIO (S3-compatible storage, порти 9000, 9001)

### 4. Створення суперюзера

```bash
docker-compose exec backend python manage.py createsuperuser
```

### 5. Створення тестових планів підписки

```bash
docker-compose exec backend python manage.py shell

from apps.subscriptions.models import Plan

# Free plan
Plan.objects.create(
    name="Free",
    slug="free",
    price_monthly=0,
    price_yearly=0,
    plan_type='free',
    max_users=1,
    max_documents=10,
    max_photos_per_month=100,
    max_messages_per_month=100,
    max_conversations_per_month=50,
    max_integrations=1,  # Only Telegram allowed
    max_storage_mb=100,
    has_watermark=True,
    is_public=True
)

# Starter plan
Plan.objects.create(
    name="Starter",
    slug="starter",
    price_monthly=14.99,
    price_yearly=149.90,
    max_users=3,
    max_documents=100,
    max_photos_per_month=1000,
    max_messages_per_month=500,
    max_integrations=2,  # Telegram + WhatsApp
    max_storage_mb=1000,
    has_watermark=False,
    features=["telegram", "whatsapp"],
    is_public=True
)

# Professional plan
Plan.objects.create(
    name="Professional",
    slug="professional",
    price_monthly=59,
    price_yearly=590,
    max_users=10,
    max_documents=1000,
    max_photos_per_month=10000,
    max_messages_per_month=5000,
    max_integrations=10,  # All integrations
    max_storage_mb=10000,
    has_watermark=False,
    features=["telegram", "whatsapp", "instagram", "google_calendar", "google_sheets", "google_reviews", "email_integration"],
    is_public=True
)

# Enterprise plan
Plan.objects.create(
    name="Enterprise",
    slug="enterprise",
    price_monthly=99,
    price_yearly=990,
    max_users=50,
    max_documents=10000,
    max_photos_per_month=100000,
    max_messages_per_month=999999,  # Unlimited
    max_integrations=999,  # Unlimited
    max_storage_mb=100000,
    has_watermark=False,
    features=["telegram", "whatsapp", "instagram", "google_calendar", "google_sheets", "google_reviews", "email_integration", "instagram_embeddings", "instagram_full_analytics", "voice_cloning"],
    is_public=True
)
```

### 6. Доступ до сервісів

- **API**: http://localhost:8000/api/
- **Admin панель**: http://localhost:8000/admin/
- **API документація**: http://localhost:8000/api/docs/ (треба додати drf-spectacular)
- **Flower (Celery)**: http://localhost:5555
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## API Endpoints

### Authentication

```
POST   /api/auth/register/          - Реєстрація
POST   /api/auth/login/             - Логін (JWT)
POST   /api/auth/refresh/           - Оновлення токену
POST   /api/auth/logout/            - Вихід
GET    /api/auth/me/                - Поточний користувач
PUT    /api/auth/profile/           - Оновлення профілю
```

### Subscriptions

```
GET    /api/subscriptions/plans/              - Список планів
GET    /api/subscriptions/current/            - Поточна підписка
POST   /api/subscriptions/activate-code/      - Активація коду
POST   /api/subscriptions/checkout/           - Stripe checkout
POST   /api/subscriptions/cancel/             - Скасування підписки
GET    /api/subscriptions/usage/              - Статистика використання
```

### Referrals

```
GET    /api/referrals/my-code/                - Мій реферальний код
GET    /api/referrals/stats/                  - Статистика
GET    /api/referrals/list/                   - Список рефералів
```

### Documents & Photos

```
POST   /api/documents/upload/                 - Завантаження документу
GET    /api/documents/                        - Список документів
DELETE /api/documents/{id}/                   - Видалення

POST   /api/photos/upload/                    - Завантаження фото
GET    /api/photos/                           - Список фото
```

### AI Agent

```
GET    /api/agent/prompt/                     - Отримати промпт
PUT    /api/agent/prompt/                     - Оновити промпт
POST   /api/agent/chat/                       - Відправити повідомлення
GET    /api/agent/history/                    - Історія розмов
GET    /api/agent/history/{id}/               - Деталі розмови
POST   /api/agent/test/                       - Тестування в sandbox
```

### Integrations

```
GET    /api/integrations/                     - Список інтеграцій
POST   /api/integrations/telegram/connect/    - Підключити Telegram
POST   /api/integrations/whatsapp/connect/    - Підключити WhatsApp
POST   /api/integrations/calendar/connect/    - Підключити Calendar
DELETE /api/integrations/{id}/                - Відключити
```

## Розробка

### Локальний запуск без Docker

```bash
# Створити віртуальне середовище
python -m venv venv
source venv/bin/activate  # Linux/Mac
# або
venv\Scripts\activate  # Windows

# Встановити залежності
pip install -r requirements/development.txt

# Запустити міграції
python manage.py migrate

# Запустити сервер
python manage.py runserver
```

### Celery (локально)

У окремих терміналах:

```bash
# Worker
celery -A config worker --loglevel=info

# Beat (scheduler)
celery -A config beat --loglevel=info

# Flower (monitoring)
celery -A config flower
```

### Міграції

```bash
# Створити міграції
python manage.py makemigrations

# Застосувати міграції
python manage.py migrate

# Міграції для всіх tenant schemas
python manage.py migrate_schemas
```

### Тестування

```bash
# Запустити всі тести
pytest

# З покриттям
pytest --cov=apps --cov-report=html

# Окремий додаток
pytest apps/accounts/tests/
```

### Форматування коду

```bash
# Black
black .

# isort
isort .

# flake8
flake8 .
```

## Celery Tasks

### Підписки

- `check_trial_expirations` - Щодня о 00:00 - перевірка закінчення trial періодів
- `process_subscription_billing` - Щодня о 01:00 - обробка автоматичних списань
- `check_usage_limits` - Кожну годину - перевірка лімітів
- `reset_monthly_usage` - Автоматично - скидання місячних лімітів

### Реферали

- `check_referral_rewards` - Щодня о 02:00 - перевірка досягнення 50 активних рефералів
- `update_referral_stats` - Кожну годину - оновлення статистики

### Документи

- `process_document` - Асинхронна обробка документів (парсинг, OCR, векторизація)
- `process_photo` - Асинхронна обробка фото (Google Vision API, векторизація)
- `cleanup_old_files` - Щонеділі о 03:00 - видалення старих файлів

### Векторизація

- `create_embeddings` - Створення векторів з тексту (OpenAI ada-002)
- `rebuild_vector_store` - Повна перебудова векторного сховища

## Безпека

- ✅ JWT автентифікація
- ✅ Rate limiting (100 req/hour для анонімів, 1000 req/hour для юзерів)
- ✅ CORS налаштований
- ✅ Шифрування credentials для інтеграцій
- ✅ SQL Injection захист (Django ORM)
- ✅ XSS захист (DRF автоматично екранує)
- ✅ Multi-tenant ізоляція даних

## Deployment (Production)

### 1. Налаштування змінних

```env
DEBUG=False
ALLOWED_HOSTS=api.yourdomain.com
DATABASE_URL=postgresql://user:pass@db-host:5432/sloth
REDIS_URL=redis://redis-host:6379/0

# SSL
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Sentry
SENTRY_DSN=your-sentry-dsn
```

### 2. Використовуйте Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 3. Nginx як reverse proxy

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/media/;
    }
}
```

### 4. Supervisor для Celery

```ini
[program:celery_worker]
command=/app/venv/bin/celery -A config worker --loglevel=info
directory=/app
user=www-data
autostart=true
autorestart=true

[program:celery_beat]
command=/app/venv/bin/celery -A config beat --loglevel=info
directory=/app
user=www-data
autostart=true
autorestart=true
```

## Моніторинг

- **Flower** - Celery tasks monitoring (http://localhost:5555)
- **Sentry** - Error tracking
- **PostgreSQL slow query log** - Performance monitoring
- **Prometheus + Grafana** - Опціонально

## Troubleshooting

### Problem: Не можу підключитися до PostgreSQL

```bash
# Перевірте чи запущений контейнер
docker-compose ps

# Перевірте логи
docker-compose logs postgres

# Перевірте підключення
docker-compose exec postgres psql -U sloth -d sloth
```

### Problem: Celery tasks не виконуються

```bash
# Перевірте чи запущений worker
docker-compose logs celery

# Перевірте Redis підключення
docker-compose exec redis redis-cli ping

# Перевірте Flower
http://localhost:5555
```

### Problem: pgvector не працює

```bash
# Підключіться до PostgreSQL
docker-compose exec postgres psql -U sloth -d sloth

# Перевірте чи встановлено extension
SELECT * FROM pg_extension WHERE extname = 'vector';

# Якщо немає - встановіть
CREATE EXTENSION IF NOT EXISTS vector;
```

## Ліцензія

Proprietary - всі права захищені

## Підтримка

Для питань та багів звертайтеся до команди розробки.
