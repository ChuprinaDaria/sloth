# Швидкий Старт: SSL для sloth-ai.lazysoft.pl

## Команди для Копіювання (Copy-Paste Ready)

### 1. Отримати Сертифікати

```bash
# Webroot метод (рекомендовано)
sudo mkdir -p /var/www/certbot
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d sloth-ai.lazysoft.pl \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email
```

### 2. Встановити Nginx Конфігурацію

```bash
cd /opt/sloth
sudo cp nginx-system-config.conf /etc/nginx/sites-available/sloth-ai.conf
sudo ln -sf /etc/nginx/sites-available/sloth-ai.conf /etc/nginx/sites-enabled/sloth-ai.conf
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Перевірити Сертифікати

```bash
sudo ls -la /etc/letsencrypt/live/sloth-ai.lazysoft.pl/
sudo certbot certificates
```

### 4. Тест HTTPS

```bash
curl -I https://sloth-ai.lazysoft.pl
```

---

## OAuth Callback URLs (Оновіть в провайдерах)

### Google OAuth
```
https://sloth-ai.lazysoft.pl/api/auth/google/callback/
```

### Facebook/Instagram
```
https://sloth-ai.lazysoft.pl/api/auth/facebook/callback/
```

### Stripe Webhooks
```
https://sloth-ai.lazysoft.pl/webhooks/stripe/
```

### Telegram Webhook
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/"
```

---

## Production Environment Variables

Додайте в `/opt/sloth/backend/.env`:

```bash
BACKEND_URL=https://sloth-ai.lazysoft.pl
FRONTEND_URL=https://sloth-ai.lazysoft.pl
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl,www.lazysoft.pl
CORS_ALLOWED_ORIGINS=https://sloth-ai.lazysoft.pl

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

---

## Перезапуск Сервісів

```bash
cd /opt/sloth
docker-compose down
docker-compose up -d
docker-compose logs -f backend
```

---

**Детальна документація**: [SSL_SETUP.md](./SSL_SETUP.md)
