# Чеклист для деплою Sloth AI

## ✅ Локальне тестування (виконано)

- [x] Docker контейнери запускаються
- [x] Backend API працює (порт 8000)
- [x] Frontend працює (порт 5173)
- [x] PostgreSQL підключений та healthy
- [x] Redis підключений та healthy
- [x] Celery Worker працює
- [x] Celery Beat працює
- [x] Flower (Celery monitoring) працює (порт 5555)
- [x] Health endpoint `/health/` додано та працює
- [x] API endpoints відповідають коректно
- [ ] MinIO має проблему з архітектурою CPU (не критично для локального тестування)

## 📋 Перед деплоєм

### 1. Налаштування Production .env файлів

**Backend:** `backend/.env.production`
```bash
cd backend
cp .env.production.example .env.production
nano .env.production
```

**Frontend:** `.env.production` (або `.env.production.local`)
```bash
cp .env.production.example .env.production.local
nano .env.production.local
```

### 2. Обов'язкові змінні для production

#### Backend (.env.production)
- [ ] `SECRET_KEY` - згенерувати новий безпечний ключ
- [ ] `DEBUG=False`
- [ ] `ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl,www.lazysoft.pl`
- [ ] `POSTGRES_PASSWORD` - сильний пароль для БД
- [ ] `REDIS_PASSWORD` - пароль для Redis
- [ ] `OPENAI_API_KEY` - ваш OpenAI API ключ
- [ ] `STRIPE_SECRET_KEY` - production Stripe ключ
- [ ] `STRIPE_PUBLISHABLE_KEY` - production Stripe публічний ключ
- [ ] `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- [ ] `GOOGLE_CLIENT_ID` та `GOOGLE_CLIENT_SECRET` - Google OAuth
- [ ] `FACEBOOK_APP_ID` та `FACEBOOK_APP_SECRET` - Facebook/Instagram
- [ ] `SENTRY_DSN` - для моніторингу помилок (опціонально)

#### Frontend (.env.production.local)
- [ ] `VITE_API_URL=https://sloth-ai.lazysoft.pl/api`
- [ ] `VITE_STRIPE_PUBLIC_KEY=pk_live_...` - production Stripe ключ
- [ ] `VITE_ENV=production`

### 3. SSL сертифікати

```bash
# Створити директорії
mkdir -p certbot/conf certbot/www

# Отримати сертифікати (спочатку staging для тестування)
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --staging \
  -d sloth-ai.lazysoft.pl

# Після успішного тестування - production сертифікати
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  -d sloth-ai.lazysoft.pl
```

### 4. DNS налаштування

- [ ] DNS A record: `sloth-ai.lazysoft.pl` → IP сервера
- [ ] DNS A record: `lazysoft.pl` → IP сервера (опціонально)
- [ ] DNS A record: `www.lazysoft.pl` → IP сервера (опціонально)

### 5. Firewall налаштування

```bash
# Дозволити тільки необхідні порти
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (для Let's Encrypt)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

## 🚀 Деплой

### Використання deploy скрипта

```bash
# Перший деплой
chmod +x deploy.sh
./deploy.sh init

# Оновлення
./deploy.sh update

# Перезапуск сервісів
./deploy.sh restart

# Перегляд логів
./deploy.sh logs

# Статус сервісів
./deploy.sh status

# Backup
./deploy.sh backup
```

### Ручний деплой

```bash
# 1. Запустити сервіси
docker-compose -f docker-compose.prod.yml up -d --build

# 2. Міграції БД
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 3. Створити суперкористувача
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# 4. Створити default subscription plans
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_default_plans

# 5. Зібрати static файли
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## ✅ Після деплою

### 1. Перевірка сервісів

```bash
# Статус всіх контейнерів
docker-compose -f docker-compose.prod.yml ps

# Health check
curl https://sloth-ai.lazysoft.pl/health/

# API check
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Frontend check
curl https://sloth-ai.lazysoft.pl/
```

### 2. Налаштування webhooks

- [ ] **Stripe Webhook:** `https://sloth-ai.lazysoft.pl/webhooks/stripe/`
  - Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`

- [ ] **Telegram Bot Webhook:**
```bash
curl -F "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/<bot_id>/" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

- [ ] **Instagram Webhook:** Налаштувати в Meta Developer Console
  - Callback URL: `https://sloth-ai.lazysoft.pl/webhooks/instagram/`
  - Verify Token: (з FACEBOOK_WEBHOOK_VERIFY_TOKEN)

### 3. Моніторинг

- [ ] Налаштувати Sentry для відстеження помилок
- [ ] Перевірити Celery Flower (доступ через SSH tunnel)
- [ ] Налаштувати автоматичні бекапи БД
- [ ] Налаштувати моніторинг дискового простору
- [ ] Налаштувати моніторинг пам'яті та CPU

## 🔧 Troubleshooting

### Проблеми з SSL

```bash
# Перевірити сертифікати
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates

# Оновити сертифікати вручну
docker-compose -f docker-compose.prod.yml exec certbot certbot renew
```

### Проблеми з БД

```bash
# Перевірити підключення
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell

# Міграції
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Проблеми з static файлами

```bash
# Зібрати static файли
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## 📝 Нотатки

- Health endpoint `/health/` додано та працює
- Production конфігурація готова
- MinIO має проблему з архітектурою CPU на локальній машині (не критично, в production використовується S3)
- Всі основні сервіси працюють коректно

