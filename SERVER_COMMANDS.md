# Команди для роботи зі Sloth AI на сервері

## 📍 Швидкий старт

```bash
# Підключення до сервера
ssh root@128.140.65.237

# Перехід до проєкту
cd /opt/sloth
```

## 🚀 Деплой

### Перший деплой

```bash
cd /opt/sloth

# 1. Налаштувати .env файли
nano backend/.env.production
nano .env.production.local

# 2. Отримати SSL сертифікати (див. DEPLOY_TO_EXISTING_SERVER.md)

# 3. Запустити деплой
./QUICK_DEPLOY.sh
# або
./deploy.sh init
```

### Оновлення

```bash
cd /opt/sloth
git pull origin main
./deploy.sh update
```

## 📊 Статус та моніторинг

```bash
cd /opt/sloth

# Статус всіх сервісів
docker-compose -f docker-compose.prod.yml ps

# Детальний статус
./deploy.sh status

# Логи (всі сервіси)
./deploy.sh logs

# Логи конкретного сервісу
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f celery
```

## 🔄 Управління сервісами

```bash
cd /opt/sloth

# Перезапуск всіх сервісів
./deploy.sh restart

# Перезапуск конкретного сервісу
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart nginx
docker-compose -f docker-compose.prod.yml restart celery

# Зупинка
docker-compose -f docker-compose.prod.yml down

# Запуск
docker-compose -f docker-compose.prod.yml up -d
```

## 🗄️ База даних

```bash
cd /opt/sloth

# Міграції
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Shell БД
docker-compose -f docker-compose.prod.yml exec backend python manage.py dbshell

# Створити суперкористувача
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Створити default plans
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_default_plans
```

## 💾 Backup

```bash
cd /opt/sloth

# Автоматичний backup (БД + media)
./deploy.sh backup

# Ручний backup БД
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U sloth sloth > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup media
docker run --rm \
  -v sloth_media_volume:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

## 🔍 Перевірка

```bash
# Health check
curl https://sloth-ai.lazysoft.pl/health/

# API check
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Frontend check
curl -I https://sloth-ai.lazysoft.pl/

# З сервера
curl http://localhost:8000/health/
curl http://localhost:8000/api/subscriptions/plans/
```

## 🔒 SSL сертифікати

```bash
cd /opt/sloth

# Перевірити сертифікати
docker-compose -f docker-compose.prod.yml exec certbot certbot certificates

# Оновити вручну
docker-compose -f docker-compose.prod.yml exec certbot certbot renew

# Перезавантажити nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

## 🧹 Очистка

```bash
cd /opt/sloth

# Видалити невикористані образи
docker image prune -a

# Видалити невикористані volumes
docker volume prune

# Видалити невикористані контейнери
docker container prune

# Повна очистка (ОБЕРЕЖНО!)
docker system prune -a --volumes
```

## 📈 Моніторинг ресурсів

```bash
# Дисковий простір
df -h

# Пам'ять
free -h

# Docker статистика
docker stats

# Використання диску Docker
docker system df
```

## 🆘 Troubleshooting

### Backend не запускається

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Проблеми з БД

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml ps postgres
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

### 502 Bad Gateway

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml ps backend
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml restart backend nginx
```

### Static files не завантажуються

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py collectstatic --noinput
```

### Celery tasks не виконуються

```bash
cd /opt/sloth
docker-compose -f docker-compose.prod.yml logs celery
docker-compose -f docker-compose.prod.yml restart celery
```

## 🔐 Доступ до Celery Flower

```bash
# На локальній машині
ssh -L 5555:localhost:5555 root@128.140.65.237

# Потім відкрити в браузері
# http://localhost:5555
```

## 📝 Корисні команди

```bash
# Перевірити чи працює проєкт
cd /opt/sloth && docker-compose -f docker-compose.prod.yml ps

# Перевірити порти
netstat -tulpn | grep LISTEN
# або
ss -tulpn | grep LISTEN

# Перевірити firewall
ufw status

# Перевірити Docker
docker ps
docker-compose -f docker-compose.prod.yml ps
```

## 🌐 Webhooks налаштування

### Stripe
- URL: `https://sloth-ai.lazysoft.pl/webhooks/stripe/`
- Events: `checkout.session.completed`, `customer.subscription.updated`, etc.

### Telegram
```bash
curl -F "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/<bot_id>/" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

### Instagram
- Meta Developer Console
- Callback: `https://sloth-ai.lazysoft.pl/webhooks/instagram/`

---

**Швидка довідка для сервера LazysoftWEB**
