# Налаштування Sloth AI з кастомними портами

Якщо стандартні порти (80, 443, 8000, 5173) зайняті іншими проєктами, використовуйте цю інструкцію.

## Використання кастомних портів

**Backend:** `18000` (замість 8000)  
**Frontend:** `15173` (замість 5173)

## Покрокова інструкція

### 1. Використати docker-compose з кастомними портами

```bash
cd /opt/sloth

# Скопіювати файл з кастомними портами
cp docker-compose.prod.yml.custom-ports docker-compose.prod.yml

# Або використати безпосередньо
docker-compose -f docker-compose.prod.yml.custom-ports up -d --build
```

### 2. Налаштувати системний nginx

```bash
# Скопіювати конфігурацію
sudo cp nginx-system-config.conf /etc/nginx/sites-available/sloth-ai.conf

# Активувати
sudo ln -s /etc/nginx/sites-available/sloth-ai.conf /etc/nginx/sites-enabled/

# Перевірити конфігурацію
sudo nginx -t

# Перезавантажити nginx
sudo systemctl reload nginx
```

### 3. Отримати SSL сертифікати

```bash
cd /opt/sloth
mkdir -p certbot/conf certbot/www

# Staging (тест)
sudo docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --staging \
  -d sloth-ai.lazysoft.pl

# Production
sudo docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  -d sloth-ai.lazysoft.pl
```

### 4. Оновити nginx конфігурацію з шляхами до сертифікатів

```bash
sudo nano /etc/nginx/sites-available/sloth-ai.conf
```

Змініть шляхи до сертифікатів:
```nginx
ssl_certificate /opt/sloth/certbot/conf/live/sloth-ai.lazysoft.pl/fullchain.pem;
ssl_certificate_key /opt/sloth/certbot/conf/live/sloth-ai.lazysoft.pl/privkey.pem;
```

Або якщо сертифікати в стандартному місці:
```nginx
ssl_certificate /etc/letsencrypt/live/sloth-ai.lazysoft.pl/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/sloth-ai.lazysoft.pl/privkey.pem;
```

### 5. Перезавантажити nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Перевірити роботу

```bash
# Health check через системний nginx
curl https://sloth-ai.lazysoft.pl/health/

# Пряме підключення до backend (для тестування)
curl http://localhost:18000/health/

# Пряме підключення до frontend (для тестування)
curl http://localhost:15173/
```

## Зміна портів (якщо потрібні інші)

Якщо порти 18000 або 15173 теж зайняті, змініть їх у файлах:

1. **docker-compose.prod.yml.custom-ports:**
   ```yaml
   backend:
     ports:
       - "ВАШ_ПОРТ:8000"  # Наприклад "28000:8000"
   
   frontend:
     ports:
       - "ВАШ_ПОРТ:5173"  # Наприклад "25173:5173"
   ```

2. **nginx-system-config.conf:**
   ```nginx
   location / {
       proxy_pass http://localhost:ВАШ_ПОРТ_FRONTEND;
   }
   
   location /api/ {
       proxy_pass http://localhost:ВАШ_ПОРТ_BACKEND;
   }
   ```

## Перевірка зайнятих портів

```bash
# Перевірити які порти зайняті
sudo netstat -tulpn | grep LISTEN
# або
sudo ss -tulpn | grep LISTEN

# Перевірити конкретний порт
sudo netstat -tuln | grep :18000
sudo netstat -tuln | grep :15173
```

## Troubleshooting

### Backend не доступний на порту 18000

```bash
# Перевірити чи запущений контейнер
docker ps | grep sloth_backend

# Перевірити логи
docker logs sloth_backend

# Перевірити порт
curl http://localhost:18000/health/
```

### Frontend не доступний на порту 15173

```bash
# Перевірити чи запущений контейнер
docker ps | grep sloth_frontend

# Перевірити логи
docker logs sloth_frontend

# Перевірити порт
curl http://localhost:15173/
```

### Nginx не може підключитися

```bash
# Перевірити nginx конфігурацію
sudo nginx -t

# Перевірити логи nginx
sudo tail -f /var/log/nginx/error.log

# Перевірити чи доступні порти з nginx
curl http://localhost:18000/health/
curl http://localhost:15173/
```

## Після налаштування

✅ Backend доступний на `http://localhost:18000`  
✅ Frontend доступний на `http://localhost:15173`  
✅ Через системний nginx: `https://sloth-ai.lazysoft.pl`  
✅ SSL сертифікати встановлені  
✅ Nginx конфігурація активна

---

**Готово!** Sloth AI працює на кастомних портах і доступний через системний nginx.

