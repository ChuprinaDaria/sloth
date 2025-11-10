# Інструкції для оновлення на сервері

## Якщо помилки залишаються після оновлення коду

### 1. Перевірте чи код оновився

```bash
cd /opt/sloth
git pull origin main
git log --oneline -5  # Перевірте останні коміти
```

### 2. Перевірте BACKEND_URL в .env

```bash
# В Docker
docker compose exec backend env | grep BACKEND_URL

# Або в файлі
cat backend/.env | grep BACKEND_URL
```

**Має бути:**
```env
BACKEND_URL=https://sloth-ai.lazysoft.pl
```

**НЕ має бути:**
```env
BACKEND_URL=https://sloth-ai.lazysoft.pl/  # ❌ Без слешу в кінці!
```

### 3. Перезапустіть сервіси

```bash
cd /opt/sloth
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d backend frontend nginx
```

### 4. Перевірте логи для Telegram помилки

```bash
# Логи бекенду
docker compose -f docker-compose.prod.yml logs backend --tail=100 | grep -i telegram

# Або всі помилки
docker compose -f docker-compose.prod.yml logs backend --tail=100 | grep -i error
```

### 5. Перевірте Google OAuth redirect URI

В Google Cloud Console → Credentials → OAuth 2.0 Client ID → Edit:

**Authorized redirect URIs** має містити ТІЛЬКИ:
```
https://sloth-ai.lazysoft.pl/api/integrations/calendar/callback/
```

**Видаліть всі інші URI** (scopes та неіснуючі endpoints).

### 6. Якщо Telegram все ще не працює

Перевірте чи правильно налаштований bot token:
- Токен має бути валідним
- Бот має бути створений через @BotFather
- Перевірте чи токен не застарів

### 7. Перевірка після оновлення

```bash
# 1. Перевірте чи код оновився
cd /opt/sloth
git log --oneline -1

# 2. Перевірте чи сервіси запущені
docker compose -f docker-compose.prod.yml ps

# 3. Перевірте логи
docker compose -f docker-compose.prod.yml logs backend --tail=50

# 4. Перевірте чи працює API
curl https://sloth-ai.lazysoft.pl/api/health/
```

### 8. Якщо все ще помилки

Перевірте детальні логи:
```bash
# Всі помилки з бекенду
docker compose -f docker-compose.prod.yml logs backend 2>&1 | grep -i "error\|exception\|traceback" | tail -50

# Помилки з конкретного запиту
docker compose -f docker-compose.prod.yml logs backend --since 5m | grep -A 10 "telegram\|oauth"
```

