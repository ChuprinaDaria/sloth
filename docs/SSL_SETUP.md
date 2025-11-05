# SSL Сертифікати для Sloth AI (sloth-ai.lazysoft.pl)

## Огляд

Цей документ описує як налаштувати SSL сертифікати Let's Encrypt для sloth-ai.lazysoft.pl субдомену, подібно до існуючого налаштування для voicebot.lazysoft.pl.

## Передумови

- Root/sudo доступ до сервера
- Налаштований DNS A-запис для sloth-ai.lazysoft.pl
- Встановлений certbot
- Nginx встановлений і працює

## Крок 1: Отримання SSL Сертифікатів

### Варіант A: Standalone метод (якщо nginx зупинений)

```bash
# Зупиніть nginx щоб звільнити порт 80
sudo systemctl stop nginx

# Отримайте сертифікати
sudo certbot certonly --standalone \
  -d sloth-ai.lazysoft.pl \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email

# Запустіть nginx знову
sudo systemctl start nginx
```

### Варіант B: Webroot метод (рекомендовано, якщо nginx працює)

```bash
# Створіть директорію для ACME challenge якщо не існує
sudo mkdir -p /var/www/certbot

# Отримайте сертифікати
sudo certbot certonly --webroot \
  -w /var/www/certbot \
  -d sloth-ai.lazysoft.pl \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email
```

### Варіант C: Використання існуючого wildcard сертифікату

Якщо у вас є wildcard сертифікат для `*.lazysoft.pl`, ви можете використати його:

```bash
# Перевірте чи існує wildcard сертифікат
ls -la /etc/letsencrypt/live/lazysoft.pl/

# Якщо існує, змініть конфігурацію nginx для використання wildcard сертифікату
```

## Крок 2: Встановлення Nginx Конфігурації

```bash
# Скопіюйте конфігурацію на сервер
sudo cp /opt/sloth/nginx-system-config.conf /etc/nginx/sites-available/sloth-ai.conf

# Створіть symbolic link
sudo ln -sf /etc/nginx/sites-available/sloth-ai.conf /etc/nginx/sites-enabled/sloth-ai.conf

# Видаліть дефолтну конфігурацію якщо існує
sudo rm -f /etc/nginx/sites-enabled/default
```

## Крок 3: Перевірка та Перезавантаження Nginx

```bash
# Перевірте синтаксис конфігурації
sudo nginx -t

# Якщо все ОК, перезавантажте nginx
sudo systemctl reload nginx

# Або повне перезавантаження
sudo systemctl restart nginx
```

## Крок 4: Перевірка Сертифікатів

```bash
# Перевірте що сертифікати створені
sudo ls -la /etc/letsencrypt/live/sloth-ai.lazysoft.pl/

# Повинні бути:
# - cert.pem       - основний сертифікат
# - chain.pem      - ланцюжок сертифікатів
# - fullchain.pem  - повний ланцюжок (cert + chain)
# - privkey.pem    - приватний ключ

# Перевірте термін дії сертифікату
sudo certbot certificates
```

## Крок 5: Налаштування Автоматичного Оновлення

```bash
# Перевірте що certbot timer активний
sudo systemctl status certbot.timer

# Якщо не активний, увімкніть його
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Тест автоматичного оновлення (dry run)
sudo certbot renew --dry-run
```

## Крок 6: Налаштування OAuth Callback URLs

Після отримання SSL сертифікатів, **оновіть OAuth callback URLs** у всіх OAuth провайдерах:

### Google OAuth (Calendar + Sheets)

1. Відкрийте [Google Cloud Console](https://console.cloud.google.com/)
2. Виберіть ваш проєкт
3. Перейдіть до **APIs & Services** → **Credentials**
4. Оберіть OAuth 2.0 Client ID для Sloth AI
5. Додайте до **Authorized redirect URIs**:
   ```
   https://sloth-ai.lazysoft.pl/api/auth/google/callback/
   https://sloth-ai.lazysoft.pl/google/callback
   ```
6. Збережіть зміни

### Facebook/Instagram API

1. Відкрийте [Facebook Developers](https://developers.facebook.com/)
2. Виберіть ваш додаток
3. Перейдіть до **Settings** → **Basic**
4. Додайте до **App Domains**: `sloth-ai.lazysoft.pl`
5. У **Facebook Login** → **Settings**:
   ```
   Valid OAuth Redirect URIs:
   https://sloth-ai.lazysoft.pl/api/auth/facebook/callback/
   ```

### Stripe Webhooks

1. Відкрийте [Stripe Dashboard](https://dashboard.stripe.com/)
2. Перейдіть до **Developers** → **Webhooks**
3. Оновіть endpoint URL:
   ```
   https://sloth-ai.lazysoft.pl/webhooks/stripe/
   ```

### Telegram Webhook

```bash
# Оновіть webhook URL через Telegram API
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/"
```

## Крок 7: Оновлення Environment Variables

На production сервері створіть файл `.env` з HTTPS URLs:

```bash
# На сервері в /opt/sloth/backend/.env
BACKEND_URL=https://sloth-ai.lazysoft.pl
FRONTEND_URL=https://sloth-ai.lazysoft.pl
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl,www.lazysoft.pl
CORS_ALLOWED_ORIGINS=https://sloth-ai.lazysoft.pl

# Security Settings для HTTPS
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

## Крок 8: Перезапуск Сервісів

```bash
# Перезапустіть Docker контейнери з новими environment variables
cd /opt/sloth
docker-compose down
docker-compose up -d

# Перевірте логи
docker-compose logs -f backend
```

## Тестування

### 1. Перевірка HTTPS

```bash
# Перевірте що сайт працює через HTTPS
curl -I https://sloth-ai.lazysoft.pl

# Повинно бути: HTTP/2 200
```

### 2. Перевірка SSL Rating

Відкрийте [SSL Labs Test](https://www.ssllabs.com/ssltest/) і перевірте `sloth-ai.lazysoft.pl`

Очікується оцінка: **A або A+**

### 3. Перевірка Redirect HTTP → HTTPS

```bash
# Має перенаправити на HTTPS
curl -L http://sloth-ai.lazysoft.pl
```

### 4. Перевірка OAuth Flow

- Спробуйте увійти через Google OAuth
- Перевірте що callback працює правильно
- Перевірте логи Django для помилок

## Troubleshooting

### Проблема: Certbot не може отримати сертифікат

**Помилка**: `Connection refused` або `Timeout`

**Рішення**:
```bash
# Перевірте що DNS працює
dig sloth-ai.lazysoft.pl

# Перевірте що порт 80 відкритий
sudo netstat -tulpn | grep :80

# Перевірте firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Проблема: Nginx не запускається

**Помилка**: `nginx: [emerg] cannot load certificate`

**Рішення**:
```bash
# Перевірте що файли сертифікатів існують
ls -la /etc/letsencrypt/live/sloth-ai.lazysoft.pl/

# Перевірте права доступу
sudo chmod 755 /etc/letsencrypt/live/
sudo chmod 755 /etc/letsencrypt/archive/
```

### Проблема: OAuth callbacks не працюють

**Симптоми**: `redirect_uri_mismatch` помилка

**Рішення**:
1. Переконайтеся що callback URLs містять **точний** протокол `https://`
2. Перевірте що немає trailing slash (`/`) якщо провайдер його не очікує
3. Перевірте Django ALLOWED_HOSTS та CORS налаштування

## Структура Файлів Сертифікатів

```
/etc/letsencrypt/
├── live/
│   ├── sloth-ai.lazysoft.pl/
│   │   ├── cert.pem -> ../../archive/sloth-ai.lazysoft.pl/cert1.pem
│   │   ├── chain.pem -> ../../archive/sloth-ai.lazysoft.pl/chain1.pem
│   │   ├── fullchain.pem -> ../../archive/sloth-ai.lazysoft.pl/fullchain1.pem
│   │   └── privkey.pem -> ../../archive/sloth-ai.lazysoft.pl/privkey1.pem
│   └── voicebot.lazysoft.pl/
│       └── ...
├── archive/
│   ├── sloth-ai.lazysoft.pl/
│   └── voicebot.lazysoft.pl/
└── renewal/
    ├── sloth-ai.lazysoft.pl.conf
    └── voicebot.lazysoft.pl.conf
```

## Автоматичне Оновлення

Let's Encrypt сертифікати дійсні **90 днів**. Certbot автоматично оновлює їх через:

```bash
# Systemd timer (запускається двічі на день)
/etc/systemd/system/timers.target.wants/certbot.timer

# Або cron (якщо systemd не використовується)
0 0,12 * * * certbot renew --quiet --post-hook "systemctl reload nginx"
```

## Моніторинг Сертифікатів

Налаштуйте моніторинг терміну дії сертифікатів:

```bash
# Скрипт для перевірки (створіть cron job)
#!/bin/bash
DAYS=$(certbot certificates | grep "VALID:" | grep "sloth-ai.lazysoft.pl" | awk '{print $6}')
if [ "$DAYS" -lt 30 ]; then
  echo "SSL certificate expires in $DAYS days!" | mail -s "SSL Alert" admin@lazysoft.pl
fi
```

## Резервне Копіювання

```bash
# Резервне копіювання сертифікатів
sudo tar -czf letsencrypt-backup-$(date +%Y%m%d).tar.gz /etc/letsencrypt/

# Зберігайте backup в безпечному місці
```

## Безпека

- ✅ Приватні ключі (`privkey.pem`) **НІКОЛИ** не додавайте в Git
- ✅ Права доступу: `root:root` з `0644` для публічних файлів, `0600` для приватних
- ✅ Використовуйте HSTS для примусового HTTPS
- ✅ Регулярно оновлюйте certbot: `sudo apt update && sudo apt upgrade certbot`

## Додаткові Ресурси

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Certbot Documentation](https://certbot.eff.org/)
- [Nginx SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Test](https://www.ssllabs.com/ssltest/)

---

**Примітка**: Після успішного налаштування SSL, всі HTTP запити автоматично перенаправляються на HTTPS завдяки конфігурації nginx.
