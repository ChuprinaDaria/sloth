# Вирішення помилки 502 Bad Gateway

## Проблема
502 Bad Gateway при доступі до `https://sloth-ai.lazysoft.pl` означає, що nginx не може підключитися до frontend контейнера.

## Перевірка

### 1. Перевірити чи працює frontend

```bash
cd /opt/sloth

# Статус frontend контейнера
docker compose -f docker-compose.prod.yml ps frontend

# Логи frontend
docker compose -f docker-compose.prod.yml logs frontend --tail=50

# Перевірити чи відповідає на порту 15173
curl http://localhost:15173/
```

### 2. Перевірити nginx конфігурацію

```bash
# Перевірити чи активна конфігурація
ls -la /etc/nginx/sites-enabled/ | grep sloth

# Перевірити конфігурацію
sudo cat /etc/nginx/sites-available/sloth-ai.conf | grep -A 5 "location /"

# Перевірити чи nginx правильний
sudo nginx -t

# Перезавантажити nginx
sudo systemctl reload nginx
```

### 3. Перевірити чи frontend слухає на правильному порту

```bash
# В контейнері
docker compose -f docker-compose.prod.yml exec frontend netstat -tuln | grep 5173

# З хоста
ss -tulpn | grep 15173
```

## Рішення

### Варіант 1: Frontend не працює

```bash
# Перезапустити frontend
docker compose -f docker-compose.prod.yml restart frontend

# Перевірити логи
docker compose -f docker-compose.prod.yml logs frontend
```

### Варіант 2: Nginx не налаштований

Якщо використовуєте кастомні порти (15173), переконайтеся що nginx налаштований:

```bash
# Скопіювати конфігурацію
sudo cp /opt/sloth/nginx-system-config.conf /etc/nginx/sites-available/sloth-ai.conf

# Активувати
sudo ln -s /etc/nginx/sites-available/sloth-ai.conf /etc/nginx/sites-enabled/

# Перевірити
sudo nginx -t

# Перезавантажити
sudo systemctl reload nginx
```

### Варіант 3: Frontend працює в dev режимі замість production

Перевірте чи frontend зібраний правильно:

```bash
# Перебілдити frontend
docker compose -f docker-compose.prod.yml build frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

### Варіант 4: Проблема з портами

Якщо frontend на порту 15173, але nginx шукає на 5173:

```bash
# Перевірити nginx конфігурацію
sudo grep -n "proxy_pass.*frontend\|proxy_pass.*5173\|proxy_pass.*15173" /etc/nginx/sites-available/sloth-ai.conf

# Має бути:
# proxy_pass http://localhost:15173;
```

## Швидка перевірка

```bash
# 1. Frontend контейнер працює?
docker compose -f docker-compose.prod.yml ps frontend

# 2. Frontend відповідає локально?
curl http://localhost:15173/

# 3. Nginx конфігурація правильна?
sudo nginx -t

# 4. Nginx перезавантажений?
sudo systemctl status nginx
```

## Детальна діагностика

```bash
# Всі логи frontend
docker compose -f docker-compose.prod.yml logs frontend

# Логи nginx
sudo tail -f /var/log/nginx/error.log

# Перевірити чи frontend слухає
docker compose -f docker-compose.prod.yml exec frontend ps aux
```

