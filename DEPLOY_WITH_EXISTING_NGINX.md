# Деплой Sloth AI з існуючим nginx на сервері

Якщо на сервері вже працює системний nginx (для інших проєктів), є два варіанти:

## Варіант 1: Використати існуючий nginx (рекомендовано)

### 1. Змінити docker-compose.prod.yml

Вимкнути nginx контейнер з docker-compose і використати системний nginx:

```yaml
# Закоментувати nginx сервіс в docker-compose.prod.yml
# nginx:
#   image: nginx:alpine
#   ...
```

### 2. Додати конфігурацію в системний nginx

Створити файл `/etc/nginx/sites-available/sloth-ai.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name sloth-ai.lazysoft.pl;

    # Let's Encrypt ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name sloth-ai.lazysoft.pl;

    # SSL Certificates
    ssl_certificate /etc/letsencrypt/live/sloth-ai.lazysoft.pl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sloth-ai.lazysoft.pl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Admin
    location /admin/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Webhooks
    location /webhooks/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Health
    location /health/ {
        proxy_pass http://localhost:8000;
        access_log off;
    }
}
```

### 3. Активувати конфігурацію

```bash
ln -s /etc/nginx/sites-available/sloth-ai.conf /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4. Змінити docker-compose.prod.yml

Змінити порти для frontend і backend, щоб вони були доступні з хост-машини:

```yaml
backend:
  ports:
    - "8000:8000"  # Вже є

frontend:
  ports:
    - "5173:5173"  # Додати якщо немає
```

## Варіант 2: Використати окремі порти (альтернатива)

Якщо хочете зберегти окремий nginx контейнер, змініть порти:

```yaml
nginx:
  ports:
    - "8080:80"    # HTTP на інший порт
    - "8443:443"   # HTTPS на інший порт
```

Потім налаштуйте системний nginx як reverse proxy на порти 8080/8443.

## Швидке рішення (тимчасово)

Якщо хочете швидко запустити для тестування:

```bash
# Натисніть 'y' щоб продовжити
# Nginx контейнер не запуститься (порт зайнятий)
# Але backend і frontend будуть працювати на портах 8000 і 5173

# Потім отримайте SSL сертифікати
# І налаштуйте системний nginx як показано вище
```

---

**Рекомендація:** Використайте Варіант 1 - він простіший і ефективніший для мультисайтової конфігурації.

