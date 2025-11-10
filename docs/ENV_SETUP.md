# Налаштування змінних середовища (.env)

## Критично важливі змінні

### BACKEND_URL

**Обов'язково має бути налаштований для роботи Telegram та Google OAuth!**

```env
BACKEND_URL=https://sloth-ai.lazysoft.pl
```

**⚠️ ВАЖЛИВО:**
- Використовуйте `https://` (не `http://`)
- **БЕЗ слешу в кінці** (не `https://sloth-ai.lazysoft.pl/`)
- Має бути реальний домен (не `localhost`)

### Як перевірити на сервері:

```bash
# 1. Перевірте чи є BACKEND_URL в .env
cd /opt/sloth
cat backend/.env | grep BACKEND_URL

# 2. Якщо немає або неправильний, додайте/виправте:
# Відкрийте файл
nano backend/.env

# Додайте або змініть рядок:
BACKEND_URL=https://sloth-ai.lazysoft.pl

# Збережіть (Ctrl+O, Enter, Ctrl+X)

# 3. Перезапустіть бекенд
docker compose -f docker-compose.prod.yml restart backend
```

### Як перевірити чи працює:

```bash
# Перевірте чи змінна завантажилась
docker compose -f docker-compose.prod.yml exec backend python -c "from django.conf import settings; print(settings.BACKEND_URL)"
```

Має вивести:
```
https://sloth-ai.lazysoft.pl
```

### Якщо використовується docker-compose.prod.yml:

Перевірте чи BACKEND_URL передається в контейнер:

```bash
# Перевірте docker-compose.prod.yml
cat docker-compose.prod.yml | grep -A 5 backend:
```

Має бути:
```yaml
backend:
  environment:
    - BACKEND_URL=${BACKEND_URL}
```

Або в секції `env_file`:
```yaml
backend:
  env_file:
    - backend/.env
```

## Інші важливі змінні

### Google OAuth
```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Frontend URL
```env
FRONTEND_URL=https://sloth-ai.lazysoft.pl
```

### Database
```env
DATABASE_URL=postgresql://user:password@db:5432/sloth
```

## Повний приклад .env файлу

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,www.sloth-ai.lazysoft.pl

# URLs
BACKEND_URL=https://sloth-ai.lazysoft.pl
FRONTEND_URL=https://sloth-ai.lazysoft.pl

# Database
DATABASE_URL=postgresql://sloth:password@db:5432/sloth

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# OpenAI
OPENAI_API_KEY=sk-...

# Stripe
STRIPE_SECRET_KEY=sk_...
STRIPE_PUBLISHABLE_KEY=pk_...

# Telegram (опціонально, для дефолтного бота)
TELEGRAM_BOT_TOKEN=...

# Fernet (для шифрування credentials)
FERNET_KEY=...
```

## Після зміни .env

**Завжди перезапускайте сервіси:**

```bash
cd /opt/sloth
docker compose -f docker-compose.prod.yml restart backend
```

Або якщо зміни критичні:
```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

