# Деплой Sloth AI на існуючий сервер LazysoftWEB

## 📍 Поточна ситуація

На сервері вже є проєкти:
- `/opt/lazysoft` - існуючий сайт
- `/opt/voice_bot` - voice bot
- `/opt/containerd` - containerd

## 🎯 Рекомендована структура

Розмістити Sloth AI в `/opt/sloth` для консистентності з іншими проєктами:

```bash
/opt/
├── lazysoft/      # Існуючий сайт
├── voice_bot/     # Voice bot
└── sloth/         # Sloth AI (новий проєкт)
```

## 🚀 Покроковий деплой

### 1. Підключення до сервера

```bash
ssh root@128.140.65.237
```

### 2. Перевірка існуючих сервісів

```bash
# Перевірити чи запущені інші проєкти
cd /opt/lazysoft
docker-compose ps 2>/dev/null || echo "lazysoft не використовує docker-compose"

# Перевірити nginx конфігурацію
ls -la /etc/nginx/sites-enabled/ 2>/dev/null || echo "nginx не встановлений"
systemctl status nginx 2>/dev/null || echo "nginx не працює"
```

### 3. Створити директорію для проєкту

```bash
cd /opt
mkdir -p sloth
cd sloth
```

### 4. Клонувати репозиторій

```bash
# Якщо є git доступ
git clone https://github.com/ChuprinaDaria/sloth.git .

# Або завантажити код через інший спосіб
```

### 5. Налаштування .env файлів

**Backend:**
```bash
cd /opt/sloth
cp backend/.env.production.example backend/.env.production
nano backend/.env.production
```

**Обов'язкові змінні:**
```bash
# Django
SECRET_KEY=<згенерувати новий ключ>
DEBUG=False
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl,www.lazysoft.pl

# Database (використати унікальні паролі!)
POSTGRES_PASSWORD=sloth_secure_db_password_$(openssl rand -hex 16)
REDIS_PASSWORD=sloth_secure_redis_password_$(openssl rand -hex 16)

# URLs
DATABASE_URL=postgresql://sloth:${POSTGRES_PASSWORD}@postgres:5432/sloth
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Facebook/Instagram
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_WEBHOOK_VERIFY_TOKEN=$(openssl rand -hex 32)

# Email
EMAIL_HOST_USER=noreply@lazysoft.pl
EMAIL_HOST_PASSWORD=...

# Sentry (опціонально)
SENTRY_DSN=...
SENTRY_ENVIRONMENT=production
```

**Frontend:**
```bash
cp .env.production.example .env.production.local
nano .env.production.local
```

```bash
VITE_API_URL=https://sloth-ai.lazysoft.pl/api
VITE_STRIPE_PUBLIC_KEY=pk_live_...
VITE_ENV=production
```

### 6. Генерація SECRET_KEY

```bash
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 7. Створення .env для docker-compose

```bash
cd /opt/sloth
cat > .env << EOF
POSTGRES_PASSWORD=$(grep POSTGRES_PASSWORD backend/.env.production | cut -d'=' -f2)
REDIS_PASSWORD=$(grep REDIS_PASSWORD backend/.env.production | cut -d'=' -f2)
EOF
```

### 8. Отримання SSL сертифікатів

```bash
cd /opt/sloth
mkdir -p nginx certbot/conf certbot/www

# Створити тимчасовий nginx для ACME challenge
# (або використати існуючий nginx якщо він встановлений)

# Staging (тест)
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email \
  --staging \
  -d sloth-ai.lazysoft.pl

# Production (після успішного тесту)
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email \
  -d sloth-ai.lazysoft.pl
```

### 9. Перевірка портів

```bash
# Перевірити які порти зайняті
netstat -tulpn | grep LISTEN

# Переконатися що порти 80, 443, 8000, 5173, 5432, 6379 не конфліктують
# Sloth AI використовує внутрішні Docker мережі, тому конфліктів не буде
```

### 10. Деплой проєкту

```bash
cd /opt/sloth
chmod +x deploy.sh

# Перший деплой
./deploy.sh init
```

**Що робить `deploy.sh init`:**
- Будує всі Docker образи
- Запускає всі сервіси (postgres, redis, backend, celery, frontend, nginx)
- Виконує міграції БД
- Збирає static файли
- Створює default subscription plans

### 11. Створення суперкористувача

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py createsuperuser
```

### 12. Перевірка деплою

```bash
# Статус сервісів
cd /opt/sloth
docker-compose -f docker-compose.prod.yml ps

# Логи
./deploy.sh logs

# Health check
curl https://sloth-ai.lazysoft.pl/health/

# API check
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Frontend check
curl -I https://sloth-ai.lazysoft.pl/
```

### 13. Налаштування webhooks

**Stripe:**
1. https://dashboard.stripe.com/webhooks
2. Endpoint: `https://sloth-ai.lazysoft.pl/webhooks/stripe/`
3. Events: `checkout.session.completed`, `customer.subscription.updated`, etc.

**Telegram:**
```bash
curl -F "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/<bot_id>/" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

**Instagram:**
- Meta Developer Console
- Callback: `https://sloth-ai.lazysoft.pl/webhooks/instagram/`

## 🔧 Налаштування firewall (якщо потрібно)

```bash
# Перевірити поточний статус
ufw status

# Дозволити порти (якщо ще не дозволено)
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS

# Увімкнути (якщо не увімкнено)
ufw --force enable
```

## 📊 Моніторинг

### Перегляд логів

```bash
cd /opt/sloth

# Всі сервіси
./deploy.sh logs

# Конкретний сервіс
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f celery
```

### Статус сервісів

```bash
cd /opt/sloth
./deploy.sh status
docker-compose -f docker-compose.prod.yml ps
```

### Celery Flower (через SSH tunnel)

```bash
# На локальній машині
ssh -L 5555:localhost:5555 root@128.140.65.237

# Потім відкрити в браузері
# http://localhost:5555
```

## 🔄 Оновлення проєкту

```bash
cd /opt/sloth
git pull origin main
./deploy.sh update
```

## 💾 Backup

```bash
cd /opt/sloth

# Автоматичний backup
./deploy.sh backup

# Ручний backup БД
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U sloth sloth > backup_$(date +%Y%m%d_%H%M%S).sql
```

## ⚠️ Важливі нотатки

1. **Порти:** Sloth AI використовує Docker мережі, тому не конфліктує з іншими проєктами
2. **База даних:** Кожен проєкт має свою БД (postgres контейнер)
3. **Nginx:** Sloth AI використовує свій nginx контейнер, не конфліктує з системним nginx
4. **Диск:** Перевіряйте вільний простір: `df -h`
5. **Пам'ять:** Перевіряйте використання: `free -h`

## 🆘 Troubleshooting

### Проблеми з портами

```bash
# Перевірити зайняті порти
ss -tulpn | grep LISTEN

# Якщо порт 80/443 зайнятий системним nginx
# Sloth AI використовує свій nginx контейнер, тому конфліктів не буде
```

### Проблеми з SSL

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates
docker-compose -f docker-compose.prod.yml exec certbot certbot renew
```

### Проблеми з БД

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell
```

### Перезапуск сервісів

```bash
cd /opt/sloth
./deploy.sh restart

# Або конкретний сервіс
docker-compose -f docker-compose.prod.yml restart backend
```

## ✅ Чеклист після деплою

- [ ] Всі сервіси запущені (`docker-compose ps`)
- [ ] Health endpoint працює (`curl https://sloth-ai.lazysoft.pl/health/`)
- [ ] Frontend доступний (`https://sloth-ai.lazysoft.pl/`)
- [ ] API працює (`curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/`)
- [ ] Admin панель доступна (`https://sloth-ai.lazysoft.pl/admin/`)
- [ ] SSL сертифікати встановлені та працюють
- [ ] Створено суперкористувача
- [ ] Налаштовано Stripe webhooks
- [ ] Налаштовано Telegram webhooks (якщо потрібно)
- [ ] Налаштовано Instagram webhooks (якщо потрібно)

## 📞 Додаткова інформація

- **Сервер:** Hetzner CPX31 #109707184
- **IP:** 128.140.65.237
- **Домен:** sloth-ai.lazysoft.pl
- **Локація проєкту:** `/opt/sloth`
- **Docker Compose файл:** `docker-compose.prod.yml`

---

**Готово до деплою! 🚀**

