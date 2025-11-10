# 🔐 Environment Variables Setup Guide

## 📍 Де розміщувати .env файли

### Структура проекту:

```
/opt/sloth/                          # Production сервер
├── backend/
│   ├── .env                        ← ГОЛОВНИЙ .env для Django бекенду
│   ├── .env.example                (шаблон)
│   ├── generate_fernet_key.py      (скрипт для генерації FERNET_KEY)
│   └── ...
├── .env                            ← Docker Compose змінні (паролі БД, Redis)
├── .env.example                    (шаблон для .env)
├── docker-compose.prod.yml
└── nginx/sloth-ai.conf
```

## 🎯 Два головні .env файли:

### 1. `/opt/sloth/backend/.env`
**Призначення:** Django settings (API keys, integrations, SECRET_KEY)

**Використовується:**
- `backend` service (Django/Gunicorn)
- `celery` worker
- `celery-beat` scheduler

**Підключення:** через `env_file` в docker-compose.prod.yml:
```yaml
backend:
  env_file:
    - ./backend/.env
```

### 2. `/opt/sloth/.env`
**Призначення:** Docker Compose змінні (паролі для БД і Redis)

**Використовується:**
- docker-compose.prod.yml для підстановки `${POSTGRES_PASSWORD}`, `${REDIS_PASSWORD}`

**Підключення:** автоматично читається docker-compose

---

## 🔧 Покрокова інструкція

### Крок 1: Оновіть існуючий `/opt/sloth/backend/.env`

Якщо файл вже існує, просто додайте/оновіть необхідні параметри:

```bash
cd /opt/sloth
nano backend/.env
```

Якщо файлу немає, створіть з шаблону:
```bash
cp backend/.env.example backend/.env
nano backend/.env
```

**Обов'язкові параметри:**

```bash
# Django Settings
SECRET_KEY=CHANGE_ME_TO_RANDOM_50_CHARS  # Згенеруйте нижче ⬇️
DEBUG=False
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl,www.lazysoft.pl

# ⚠️ ОБОВ'ЯЗКОВО! Fernet Key для шифрування credentials (Telegram, Google OAuth)
FERNET_KEY=V91_g-BHq85W5Np-ePnI8-DLYjdfLlAuUVwt_BdkxmY=  # Вже згенеровано

# Database URL (docker-compose перевизначить пароль)
DATABASE_URL=postgresql://sloth:sloth_password@postgres:5432/sloth

# Redis
REDIS_URL=redis://:redis_password@redis:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://sloth-ai.lazysoft.pl,https://lazysoft.pl

# ⚠️ ОБОВ'ЯЗКОВО! OpenAI API
OPENAI_API_KEY=sk-proj-...

# Stripe (для платежів)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Telegram Bot (якщо використовуєте інтеграцію)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Google OAuth (для Calendar та Sheets)
GOOGLE_CLIENT_ID=123456789-abcdefg.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...

# URLs
BACKEND_URL=https://sloth-ai.lazysoft.pl
FRONTEND_URL=https://sloth-ai.lazysoft.pl

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@lazysoft.pl
EMAIL_HOST_PASSWORD=your-gmail-app-password
DEFAULT_FROM_EMAIL=Sloth AI <noreply@lazysoft.pl>
```

### Крок 2: Згенеруйте SECRET_KEY та FERNET_KEY

```bash
# SECRET_KEY (Django)
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# FERNET_KEY (для шифрування credentials) - вже згенерований!
# Але якщо потрібен новий:
python3 -c "import base64; import os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())"

# Або використовуйте скрипт:
cd /opt/sloth
python backend/generate_fernet_key.py
```

### Крок 3: Створіть `/opt/sloth/.env`

```bash
nano /opt/sloth/.env
```

**Вміст:**
```bash
# Паролі для Docker Compose
POSTGRES_PASSWORD=your_super_secure_database_password_here
REDIS_PASSWORD=your_super_secure_redis_password_here
```

**ВАЖЛИВО:** Ці паролі будуть автоматично підставлені в:
- `DATABASE_URL` для backend, celery, celery-beat
- `REDIS_URL` для backend, celery
- Postgres та Redis сервіси

---

## 🚀 Розгортання

### 1. Перевірте конфігурацію

```bash
cd /opt/sloth

# Перевірте що файли створені
ls -la backend/.env.production
ls -la .env

# Перевірте що FERNET_KEY є
grep FERNET_KEY backend/.env.production

# Валідація docker-compose
docker compose -f docker-compose.prod.yml config
```

### 2. Запустіть сервіси

```bash
docker compose -f docker-compose.prod.yml up -d
```

### 3. Перевірте логи

```bash
# Перевірте що бекенд запустився без помилок FERNET_KEY
docker compose -f docker-compose.prod.yml logs backend | grep -i fernet

# Загальні логи
docker compose -f docker-compose.prod.yml logs -f
```

---

## ❓ FAQ - Часті питання

### Q: Чому два .env файли?

**A:**
- **`backend/.env`** → для Django (всі API ключі, integrations)
- **`.env`** → для Docker Compose (паролі БД, які підставляються в інші контейнери)

### Q: Навіщо FERNET_KEY?

**A:** FERNET_KEY використовується для шифрування чутливих credentials користувачів:
- Telegram bot tokens
- Google OAuth credentials
- Інші API ключі, що зберігаються в БД

Без FERNET_KEY інтеграції НЕ працюватимуть!

### Q: У мене вже є backend/.env на сервері, але він не використовується?

**A:** Перевірте docker-compose.prod.yml:
```yaml
backend:
  env_file:
    - ./backend/.env  # ← Має бути саме так!
```

Якщо у вас `./backend/.env.production`, змініть на `./backend/.env` або перейменуйте файл.

### Q: Як оновити FERNET_KEY?

**A:** ⚠️ **УВАГА!** Зміна FERNET_KEY зробить неможливим розшифрування існуючих credentials.

Якщо змінюєте:
1. Користувачі мають **переввести** всі інтеграції (Telegram, Google)
2. Або міграція даних через перешифрування (складно)

### Q: Що робити якщо забув додати FERNET_KEY?

**A:** Побачите помилку:
```
ValueError: FERNET_KEY not found in settings.
Generate one with: python backend/generate_fernet_key.py
```

**Рішення:**
1. Додайте FERNET_KEY в `backend/.env.production`
2. Перезапустіть: `docker compose -f docker-compose.prod.yml restart backend`

### Q: Чи можна використовувати один .env файл?

**A:** Технічно так, але **не рекомендовано**:
- Безпека: паролі БД краще тримати окремо
- Організація: легше керувати різними типами змінних
- Docker best practice: env_file для контейнерів, .env для compose

---

## 🔒 Безпека

### ✅ Що робити:
- ✅ Додайте `.env*` в `.gitignore` (вже додано)
- ✅ Використовуйте сильні паролі (16+ символів)
- ✅ Регулярно ротуйте паролі
- ✅ Обмежте доступ до `.env` файлів: `chmod 600 backend/.env.production`
- ✅ Використовуйте різні ключі для dev та production

### ❌ Чого НЕ робити:
- ❌ НЕ коммітьте .env файли в git
- ❌ НЕ використовуйте один і той же SECRET_KEY/FERNET_KEY для dev та prod
- ❌ НЕ діліться .env файлами через незахищені канали
- ❌ НЕ змінюйте FERNET_KEY без міграції даних

---

## 📝 Checklist розгортання

- [ ] Створено/оновлено `/opt/sloth/backend/.env`
- [ ] Створено `/opt/sloth/.env`
- [ ] Згенеровано та встановлено `SECRET_KEY`
- [ ] Встановлено `FERNET_KEY=V91_g-BHq85W5Np-ePnI8-DLYjdfLlAuUVwt_BdkxmY=`
- [ ] Встановлено `OPENAI_API_KEY`
- [ ] Встановлено `TELEGRAM_BOT_TOKEN` (якщо потрібно)
- [ ] Встановлено `GOOGLE_CLIENT_ID` та `GOOGLE_CLIENT_SECRET` (якщо потрібно)
- [ ] Встановлено `POSTGRES_PASSWORD` в `.env`
- [ ] Встановлено `REDIS_PASSWORD` в `.env`
- [ ] Права доступу: `chmod 600 backend/.env .env`
- [ ] Перевірено: `docker compose -f docker-compose.prod.yml config`
- [ ] Запущено: `docker compose -f docker-compose.prod.yml up -d`
- [ ] Перевірено логи: немає помилок FERNET_KEY

---

## 🆘 Troubleshooting

### Помилка: "FERNET_KEY not found in settings"

```bash
# 1. Перевірте файл
cat backend/.env | grep FERNET_KEY

# 2. Якщо немає - додайте
echo "FERNET_KEY=V91_g-BHq85W5Np-ePnI8-DLYjdfLlAuUVwt_BdkxmY=" >> backend/.env

# 3. Перезапустіть
docker compose -f docker-compose.prod.yml restart backend celery celery-beat
```

### Помилка: Database connection refused

```bash
# Перевірте що паролі співпадають
grep POSTGRES_PASSWORD .env
grep DATABASE_URL backend/.env

# Перезапустіть БД
docker compose -f docker-compose.prod.yml restart postgres backend
```

### Telegram integration fails with 500 error

```bash
# Перевірте FERNET_KEY
docker compose -f docker-compose.prod.yml exec backend python -c "from django.conf import settings; print('FERNET_KEY:', bool(settings.FERNET_KEY))"

# Має вивести: FERNET_KEY: True
```
