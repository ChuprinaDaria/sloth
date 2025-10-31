# Backend Architecture - Sloth AI Agent Platform

## Технологічний стек

### Core
- **Django 5.0** + **Django REST Framework** - основний фреймворк
- **PostgreSQL 16** + **pgvector** - база даних з підтримкою векторного пошуку
- **Celery 5.x** + **Redis** - асинхронна обробка задач
- **JWT** (djangorestframework-simplejwt) - автентифікація

### AI & ML
- **OpenAI API** - генерація embeddings та AI відповіді
- **Google Cloud Vision API** - розпізнавання зображень
- **LangChain** - робота з LLM та векторними базами
- **Sentence Transformers** - локальні embeddings (fallback)

### Інтеграції
- **python-telegram-bot** - Telegram Bot API
- **twilio** - WhatsApp Business API
- **google-api-python-client** - Google Calendar API

### Payment
- **stripe** - обробка платежів та підписок

### Storage
- **AWS S3** / **MinIO** - зберігання файлів (документи, фото)

---

## Архітектура бази даних

### Мультитенантність (Multi-tenancy)

**Стратегія:** Schema-based isolation - кожен клієнт має окрему схему в PostgreSQL

```python
# Модель Organization (Tenant)
class Organization(models.Model):
    schema_name = models.CharField(max_length=63, unique=True)  # postgres schema
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
```

**Переваги:**
- Повна ізоляція даних між клієнтами
- Легке резервне копіювання окремих клієнтів
- Відповідність GDPR та безпека даних

---

## Структура додатків (Django Apps)

```
backend/
├── config/                      # Налаштування Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
│
├── apps/
│   ├── accounts/               # Користувачі та автентифікація
│   │   ├── models.py          # User, Organization, Profile
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   └── middleware.py      # Multi-tenant middleware
│   │
│   ├── subscriptions/          # Підписки та платежі
│   │   ├── models.py          # Plan, Subscription, ActivationCode
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tasks.py           # Celery: auto-billing, trial expiry
│   │   └── services.py        # Stripe integration
│   │
│   ├── referrals/              # Реферальна система
│   │   ├── models.py          # ReferralCode, Referral
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── services.py        # Upgrade logic
│   │
│   ├── documents/              # Завантаження та обробка файлів
│   │   ├── models.py          # Document, Photo, ProcessingJob
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tasks.py           # Celery: document parsing, OCR
│   │   └── parsers.py         # PDF, DOCX, images parsers
│   │
│   ├── embeddings/             # Векторизація та RAG
│   │   ├── models.py          # Embedding, VectorStore
│   │   ├── services.py        # OpenAI embeddings, similarity search
│   │   └── tasks.py           # Async vectorization
│   │
│   ├── agent/                  # AI Agent core
│   │   ├── models.py          # Prompt, Conversation, Message
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── services.py        # LangChain RAG pipeline
│   │   └── tasks.py           # Async AI responses
│   │
│   └── integrations/           # Зовнішні інтеграції
│       ├── models.py          # Integration, Credential
│       ├── telegram/
│       │   ├── bot.py
│       │   └── handlers.py
│       ├── whatsapp/
│       │   └── webhooks.py
│       └── google/
│           └── calendar.py
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── docker-compose.yml
├── Dockerfile
└── manage.py
```

---

## Детальні моделі даних

### 1. Accounts App

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class Organization(models.Model):
    """Організація (Tenant) - окрема схема в БД"""
    schema_name = models.CharField(max_length=63, unique=True)
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey('User', on_delete=models.PROTECT, related_name='owned_organizations')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Storage limits
    max_storage_mb = models.IntegerField(default=1000)
    used_storage_mb = models.IntegerField(default=0)

class User(AbstractUser):
    """Користувач (в public schema)"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='users')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    language = models.CharField(max_length=2, default='en')  # en, uk, pl, de

    # Referral tracking
    referral_code = models.CharField(max_length=20, unique=True)
    referred_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Profile(models.Model):
    """Профіль користувача (в tenant schema)"""
    user_id = models.IntegerField(unique=True)  # Посилання на User з public schema
    business_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=100, blank=True)  # salon, spa, clinic
    timezone = models.CharField(max_length=50, default='UTC')
    notification_email = models.EmailField()
    notification_telegram = models.BooleanField(default=True)
```

### 2. Subscriptions App

```python
class Plan(models.Model):
    """Тарифні плани (в public schema)"""
    name = models.CharField(max_length=100)  # Free, Starter, Professional, Enterprise
    slug = models.SlugField(unique=True)

    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)

    # Limits
    max_users = models.IntegerField()
    max_documents = models.IntegerField()
    max_photos_per_month = models.IntegerField()
    max_messages_per_month = models.IntegerField()
    max_storage_mb = models.IntegerField()

    # Features
    features = models.JSONField(default=list)  # ["telegram", "whatsapp", "calendar", "api"]

    # Trial
    trial_days = models.IntegerField(default=14)

    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

class Subscription(models.Model):
    """Підписка організації (в public schema)"""
    STATUS_CHOICES = [
        ('trialing', 'Trial'),
        ('active', 'Active'),
        ('past_due', 'Past Due'),
        ('canceled', 'Canceled'),
        ('unpaid', 'Unpaid'),
    ]

    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='trialing')

    # Billing
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    billing_cycle = models.CharField(max_length=10, default='monthly')  # monthly, yearly

    # Dates
    trial_start = models.DateTimeField(auto_now_add=True)
    trial_end = models.DateTimeField()
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    canceled_at = models.DateTimeField(null=True, blank=True)

    # Usage tracking
    used_messages = models.IntegerField(default=0)
    used_photos = models.IntegerField(default=0)
    used_documents = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ActivationCode(models.Model):
    """Коди активації для безкоштовних підписок (адмін)"""
    code = models.CharField(max_length=50, unique=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    duration_days = models.IntegerField()  # 30, 90, 365, або 0 для безлімітного

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    used_at = models.DateTimeField(null=True, blank=True)

    expires_at = models.DateTimeField(null=True, blank=True)
```

### 3. Referrals App

```python
class ReferralCode(models.Model):
    """Реферальний код користувача"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=20, unique=True)

    # Stats
    total_signups = models.IntegerField(default=0)
    active_referrals = models.IntegerField(default=0)  # users with active subscription

    created_at = models.DateTimeField(auto_now_add=True)

class Referral(models.Model):
    """Реферальне відношення"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),      # зареєструвався, але не активував
        ('active', 'Active'),        # активна підписка
        ('inactive', 'Inactive'),    # неактивна підписка
    ]

    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_given')
    referred = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_received')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)

class ReferralReward(models.Model):
    """Нагороди за реферали"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    referral_count = models.IntegerField()  # 50, 100, 150...
    old_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='+')
    new_plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, related_name='+')

    granted_at = models.DateTimeField(auto_now_add=True)
```

### 4. Documents App

```python
class Document(models.Model):
    """Завантажені документи (в tenant schema)"""
    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('txt', 'Text File'),
        ('xlsx', 'Excel'),
    ]

    user_id = models.IntegerField()  # Посилання на User
    title = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file_path = models.CharField(max_length=500)  # S3 URL
    file_size = models.IntegerField()  # bytes

    # Processing
    is_processed = models.BooleanField(default=False)
    processing_status = models.CharField(max_length=20, default='pending')
    processing_error = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    # Extracted content
    extracted_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

class Photo(models.Model):
    """Завантажені фото (в tenant schema)"""
    user_id = models.IntegerField()
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()

    # Vision API results
    is_processed = models.BooleanField(default=False)
    labels = models.JSONField(default=list)  # detected labels
    text = models.TextField(blank=True)  # OCR text
    objects = models.JSONField(default=list)  # detected objects
    faces = models.JSONField(default=list)  # face detection

    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ProcessingJob(models.Model):
    """Celery задачі обробки (в tenant schema)"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    celery_task_id = models.CharField(max_length=255, unique=True)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 5. Embeddings App

```python
class Embedding(models.Model):
    """Векторні представлення (в tenant schema, з pgvector)"""
    SOURCE_CHOICES = [
        ('document', 'Document'),
        ('photo', 'Photo'),
        ('message', 'Message'),
        ('prompt', 'Prompt'),
    ]

    # Source tracking
    source_type = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    source_id = models.IntegerField()

    # Content
    content = models.TextField()  # оригінальний текст

    # Vector (pgvector extension)
    vector = models.Field(db_type='vector(1536)')  # OpenAI ada-002 dimension

    # Metadata
    metadata = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            # GiST index для векторного пошуку
            models.Index(fields=['vector'], name='vector_idx', opclasses=['vector_cosine_ops']),
        ]

class VectorStore(models.Model):
    """Налаштування векторного сховища (в tenant schema)"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Settings
    embedding_model = models.CharField(max_length=100, default='text-embedding-ada-002')
    chunk_size = models.IntegerField(default=1000)
    chunk_overlap = models.IntegerField(default=200)

    # Stats
    total_embeddings = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
```

### 6. Agent App

```python
class Prompt(models.Model):
    """Користувацький промпт (в tenant schema)"""
    user_id = models.IntegerField()

    # System prompt parts
    role = models.TextField(default="You are a helpful AI assistant for a beauty salon.")
    instructions = models.TextField(blank=True)
    context = models.TextField(blank=True)

    # Settings
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=500)

    is_active = models.BooleanField(default=True)
    version = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Conversation(models.Model):
    """Розмова (в tenant schema)"""
    SOURCE_CHOICES = [
        ('web', 'Web Interface'),
        ('telegram', 'Telegram'),
        ('whatsapp', 'WhatsApp'),
    ]

    user_id = models.IntegerField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    external_id = models.CharField(max_length=255, blank=True)  # telegram chat_id, etc

    # Stats
    message_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    """Повідомлення в розмові (в tenant schema)"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()

    # Attachments
    photo = models.ForeignKey(Photo, null=True, blank=True, on_delete=models.SET_NULL)

    # RAG context used
    context_embeddings = models.ManyToManyField(Embedding, blank=True)

    # Metadata
    tokens_used = models.IntegerField(default=0)
    processing_time = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
```

### 7. Integrations App

```python
class Integration(models.Model):
    """Інтеграції (в tenant schema)"""
    TYPE_CHOICES = [
        ('telegram', 'Telegram Bot'),
        ('whatsapp', 'WhatsApp Business'),
        ('google_calendar', 'Google Calendar'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Setup'),
        ('active', 'Active'),
        ('error', 'Error'),
        ('disabled', 'Disabled'),
    ]

    user_id = models.IntegerField()
    integration_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Credentials (encrypted)
    credentials = models.JSONField(default=dict)

    # Settings
    settings = models.JSONField(default=dict)

    # Stats
    messages_received = models.IntegerField(default=0)
    messages_sent = models.IntegerField(default=0)
    last_activity = models.DateTimeField(null=True, blank=True)

    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WebhookEvent(models.Model):
    """Вебхуки від інтеграцій (в tenant schema)"""
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()

    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
```

---

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
POST   /api/subscriptions/subscribe/          - Підписка (Stripe)
POST   /api/subscriptions/cancel/             - Скасування
GET    /api/subscriptions/usage/              - Використання лімітів
```

### Admin (для генерації кодів)
```
POST   /api/admin/codes/generate/             - Генерація коду
GET    /api/admin/codes/                      - Список кодів
POST   /api/admin/subscriptions/activate/     - Ручна активація
```

### Referrals
```
GET    /api/referrals/my-code/                - Мій реферальний код
GET    /api/referrals/stats/                  - Статистика
GET    /api/referrals/list/                   - Список рефералів
```

### Documents
```
POST   /api/documents/upload/                 - Завантаження документу
GET    /api/documents/                        - Список документів
DELETE /api/documents/{id}/                   - Видалення
GET    /api/documents/{id}/status/            - Статус обробки
```

### Photos
```
POST   /api/photos/upload/                    - Завантаження фото
GET    /api/photos/                           - Список фото
DELETE /api/photos/{id}/                      - Видалення
GET    /api/photos/{id}/analysis/             - Результати аналізу
```

### Agent
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
POST   /api/integrations/webhooks/telegram/   - Telegram вебхук
POST   /api/integrations/webhooks/whatsapp/   - WhatsApp вебхук
```

---

## Celery Tasks

### Subscription Tasks
```python
# apps/subscriptions/tasks.py

@shared_task
def check_trial_expirations():
    """Перевірка закінчення trial періодів (щодня)"""
    pass

@shared_task
def process_subscription_billing():
    """Обробка автоматичних списань (щодня)"""
    pass

@shared_task
def check_usage_limits():
    """Перевірка перевищення лімітів (щогодини)"""
    pass
```

### Document Processing Tasks
```python
# apps/documents/tasks.py

@shared_task
def process_document(document_id, tenant_schema):
    """Обробка документу: парсинг, OCR, векторизація"""
    pass

@shared_task
def process_photo(photo_id, tenant_schema):
    """Обробка фото: Google Vision, векторизація"""
    pass

@shared_task
def cleanup_old_files():
    """Видалення старих файлів (щотижня)"""
    pass
```

### Embedding Tasks
```python
# apps/embeddings/tasks.py

@shared_task
def create_embeddings(content, source_type, source_id, tenant_schema):
    """Створення векторів з тексту"""
    pass

@shared_task
def rebuild_vector_store(tenant_schema):
    """Повна перебудова векторного сховища"""
    pass
```

### Referral Tasks
```python
# apps/referrals/tasks.py

@shared_task
def check_referral_rewards():
    """Перевірка досягнення 50 активних рефералів (щодня)"""
    pass

@shared_task
def update_referral_stats():
    """Оновлення статистики рефералів (щогодини)"""
    pass
```

---

## Middleware

### Multi-tenant Middleware
```python
# apps/accounts/middleware.py

class TenantMiddleware:
    """Автоматичне перемикання PostgreSQL schema на основі користувача"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Отримати tenant з JWT токену або домену
        tenant = self.get_tenant(request)

        if tenant:
            # Встановити schema для цього запиту
            from django.db import connection
            connection.set_tenant(tenant)

        response = self.get_response(request)
        return response
```

### Subscription Limit Middleware
```python
class SubscriptionLimitMiddleware:
    """Перевірка лімітів підписки"""

    def __call__(self, request):
        if request.user.is_authenticated:
            subscription = request.user.organization.subscription

            # Перевірка статусу підписки
            if subscription.status not in ['active', 'trialing']:
                return JsonResponse({'error': 'Subscription expired'}, status=402)

            # Перевірка лімітів (для певних ендпоінтів)
            if request.path.startswith('/api/agent/chat/'):
                if subscription.used_messages >= subscription.plan.max_messages_per_month:
                    return JsonResponse({'error': 'Message limit exceeded'}, status=429)

        return self.get_response(request)
```

---

## Celery Configuration

```python
# config/celery.py

from celery import Celery
from celery.schedules import crontab

app = Celery('sloth')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-trial-expirations': {
        'task': 'apps.subscriptions.tasks.check_trial_expirations',
        'schedule': crontab(hour=0, minute=0),  # Щодня о 00:00
    },
    'process-subscription-billing': {
        'task': 'apps.subscriptions.tasks.process_subscription_billing',
        'schedule': crontab(hour=1, minute=0),  # Щодня о 01:00
    },
    'check-usage-limits': {
        'task': 'apps.subscriptions.tasks.check_usage_limits',
        'schedule': crontab(minute='*/60'),  # Щогодини
    },
    'check-referral-rewards': {
        'task': 'apps.referrals.tasks.check_referral_rewards',
        'schedule': crontab(hour=2, minute=0),  # Щодня о 02:00
    },
    'update-referral-stats': {
        'task': 'apps.referrals.tasks.update_referral_stats',
        'schedule': crontab(minute='*/60'),  # Щогодини
    },
    'cleanup-old-files': {
        'task': 'apps.documents.tasks.cleanup_old_files',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Щонеділі о 03:00
    },
}
```

---

## Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: sloth
      POSTGRES_USER: sloth
      POSTGRES_PASSWORD: sloth_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
      - media:/app/media
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://sloth:sloth_pass@postgres:5432/sloth
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_CLOUD_API_KEY=${GOOGLE_CLOUD_API_KEY}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - postgres
      - redis

  celery:
    build: .
    command: celery -A config worker --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://sloth:sloth_pass@postgres:5432/sloth
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_CLOUD_API_KEY=${GOOGLE_CLOUD_API_KEY}
    depends_on:
      - postgres
      - redis

  celery-beat:
    build: .
    command: celery -A config beat --loglevel=info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://sloth:sloth_pass@postgres:5432/sloth
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  minio_data:
  media:
```

---

## Deployment Checklist

### Environment Variables
```bash
# Django
SECRET_KEY=
DEBUG=False
ALLOWED_HOSTS=api.sloth.com

# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Redis
REDIS_URL=redis://redis:6379/0

# APIs
OPENAI_API_KEY=
GOOGLE_CLOUD_API_KEY=
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=

# Storage
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=

# Telegram
TELEGRAM_BOT_TOKEN=

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_NUMBER=

# Google Calendar
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Frontend URL
FRONTEND_URL=https://sloth.com

# Email
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

### PostgreSQL Setup
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create function for tenant schemas
CREATE OR REPLACE FUNCTION create_tenant_schema(schema_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', schema_name);
    EXECUTE format('GRANT ALL ON SCHEMA %I TO sloth', schema_name);
END;
$$ LANGUAGE plpgsql;
```

### Initial Data
```python
# Create default plans
python manage.py loaddata plans

# Create superuser
python manage.py createsuperuser

# Create tenant for testing
python manage.py create_tenant --name="Test Salon" --domain="test.localhost"
```

---

## Security Considerations

1. **Multi-tenancy**: Повна ізоляція даних через PostgreSQL schemas
2. **Authentication**: JWT токени з refresh mechanism
3. **Rate Limiting**: Django REST Framework throttling
4. **File Validation**: Перевірка типів та розмірів файлів
5. **SQL Injection**: Django ORM автоматично захищає
6. **XSS**: DRF автоматично екранує дані
7. **CORS**: Налаштування для фронтенду
8. **Secrets**: Шифрування credentials для інтеграцій
9. **API Keys**: Змінні оточення, ніколи в коді
10. **Backups**: Автоматичні бекапи PostgreSQL

---

## Monitoring & Logging

- **Sentry**: Error tracking
- **Celery Flower**: Task monitoring
- **Django Debug Toolbar**: Development
- **PostgreSQL slow query log**: Performance
- **Prometheus + Grafana**: Metrics (опціонально)

---

## Testing Strategy

- **Unit Tests**: Models, services, serializers
- **Integration Tests**: API endpoints
- **Celery Tests**: Task execution
- **Load Testing**: Locust для API навантаження
- **Security Testing**: OWASP ZAP

---

Це повна архітектура бекенду. Далі я почну створювати структуру проекту та імплементацію.
