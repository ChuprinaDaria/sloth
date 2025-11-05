# Чеклист після деплою Sloth AI

## ✅ Контейнери запущені

Всі контейнери успішно запущені! Тепер виконайте наступні кроки:

## 1. Перевірка статусу сервісів

```bash
cd /opt/sloth
docker compose -f docker-compose.prod.yml ps
```

Очікуваний результат:
- ✅ sloth_backend - Up
- ✅ sloth_celery - Up
- ✅ sloth_celery_beat - Up
- ✅ sloth_frontend - Up
- ✅ sloth_postgres - Up (healthy)
- ✅ sloth_redis - Up (healthy)
- ✅ sloth_certbot - Up

## 2. Перевірка логів

```bash
# Всі сервіси
docker compose -f docker-compose.prod.yml logs --tail=50

# Конкретні сервіси
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs celery
```

## 3. Виконання міграцій

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

## 4. Створення суперкористувача

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

Введіть:
- Username: `admin` (або ваш)
- Email: `admin@lazysoft.pl`
- Password: (ваш безпечний пароль)

## 5. Створення default subscription plans

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py create_default_plans
```

## 6. Перевірка роботи сервісів

### Backend Health Check

```bash
# Через Docker network
docker compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/health/

# Через host (якщо порт відкритий)
curl http://localhost:8000/health/
```

Очікуваний результат:
```json
{"status": "healthy", "database": "connected"}
```

### Frontend

```bash
# Через Docker network
docker compose -f docker-compose.prod.yml exec frontend curl http://localhost:5173/

# Через host (якщо порт відкритий)
curl http://localhost:5173/
```

### API

```bash
curl http://localhost:8000/api/subscriptions/plans/
```

Очікуваний результат:
```json
{"count":0,"next":null,"previous":null,"results":[]}
```

## 7. Перевірка портів

```bash
# Перевірити які порти відкриті
ss -tulpn | grep -E "(8000|5173|18000|15173)"

# Або
netstat -tulpn | grep -E "(8000|5173|18000|15173)"
```

## 8. Налаштування системного nginx (якщо потрібно)

Якщо використовуєте кастомні порти (18000/15173), налаштуйте системний nginx:

```bash
# Скопіювати конфігурацію
sudo cp nginx-system-config.conf /etc/nginx/sites-available/sloth-ai.conf

# Активувати
sudo ln -s /etc/nginx/sites-available/sloth-ai.conf /etc/nginx/sites-enabled/

# Перевірити
sudo nginx -t

# Перезавантажити
sudo systemctl reload nginx
```

## 9. Отримання SSL сертифікатів

```bash
cd /opt/sloth
mkdir -p certbot/conf certbot/www

# Staging (тест)
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
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
  -d sloth-ai.lazysoft.pl
```

## 10. Налаштування webhooks

### Stripe Webhook

1. Перейдіть на https://dashboard.stripe.com/webhooks
2. Додайте endpoint: `https://sloth-ai.lazysoft.pl/webhooks/stripe/`
3. Виберіть події:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Скопіюйте webhook secret в `backend/.env.production`

### Telegram Bot Webhook

```bash
curl -F "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/<bot_id>/" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

### Instagram Webhook

- Meta Developer Console
- Callback URL: `https://sloth-ai.lazysoft.pl/webhooks/instagram/`
- Verify Token: (з `FACEBOOK_WEBHOOK_VERIFY_TOKEN`)

## 11. Фінальна перевірка

```bash
# Health через домен (після налаштування nginx)
curl https://sloth-ai.lazysoft.pl/health/

# API
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Frontend
curl -I https://sloth-ai.lazysoft.pl/
```

## Troubleshooting

### Backend не відповідає

```bash
# Перевірити логи
docker compose -f docker-compose.prod.yml logs backend

# Перевірити чи працює
docker compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/health/

# Перезапустити
docker compose -f docker-compose.prod.yml restart backend
```

### Frontend не відповідає

```bash
# Перевірити логи
docker compose -f docker-compose.prod.yml logs frontend

# Перевірити чи працює
docker compose -f docker-compose.prod.yml exec frontend curl http://localhost:5173/

# Перезапустити
docker compose -f docker-compose.prod.yml restart frontend
```

### Проблеми з БД

```bash
# Перевірити підключення
docker compose -f docker-compose.prod.yml exec backend python manage.py dbshell

# Виконати міграції
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### Celery не працює

```bash
# Перевірити логи
docker compose -f docker-compose.prod.yml logs celery

# Перевірити статус
docker compose -f docker-compose.prod.yml exec celery celery -A config inspect active
```

---

**Після виконання всіх кроків Sloth AI готовий до використання! 🎉**

