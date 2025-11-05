#!/bin/bash

# Швидкий деплой Sloth AI на існуючий сервер
# Використання: ./QUICK_DEPLOY.sh

set -e

echo "🚀 Sloth AI - Швидкий деплой на існуючий сервер"
echo ""

# Перевірка що ми в правильній директорії
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Помилка: docker-compose.prod.yml не знайдено"
    echo "   Переконайтеся що ви в директорії /opt/sloth"
    exit 1
fi

# Перевірка .env файлів
if [ ! -f "backend/.env.production" ]; then
    echo "⚠️  backend/.env.production не знайдено"
    echo "   Створіть файл на основі backend/.env.production.example"
    exit 1
fi

if [ ! -f ".env.production.local" ] && [ ! -f ".env.production" ]; then
    echo "⚠️  Frontend .env файл не знайдено"
    echo "   Створіть .env.production.local або .env.production"
    exit 1
fi

# Перевірка SSL сертифікатів
if [ ! -d "certbot/conf/live/sloth-ai.lazysoft.pl" ]; then
    echo "⚠️  SSL сертифікати не знайдено"
    echo "   Продовжую без SSL - сертифікати можна отримати після запуску сервісів"
    echo "   Див. DEPLOY_TO_EXISTING_SERVER.md для інструкцій"
    echo ""
fi

# Перевірка портів
echo "🔍 Перевірка портів..."
if netstat -tuln 2>/dev/null | grep -q ":80.*LISTEN" || ss -tuln 2>/dev/null | grep -q ":80.*LISTEN"; then
    echo "⚠️  Порт 80 вже зайнятий"
    echo "   Якщо це системний nginx, Sloth AI використовує свій nginx контейнер"
    echo "   Можливий конфлікт! Перевірте конфігурацію."
    read -p "Продовжити? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Створення .env для docker-compose
echo "📝 Створення .env для docker-compose..."
if [ ! -f ".env" ]; then
    POSTGRES_PASSWORD=$(grep "^POSTGRES_PASSWORD=" backend/.env.production | cut -d'=' -f2- | sed 's/^${POSTGRES_PASSWORD:-//' | sed 's/}$//')
    REDIS_PASSWORD=$(grep "^REDIS_PASSWORD=" backend/.env.production | cut -d'=' -f2- | sed 's/^${REDIS_PASSWORD:-//' | sed 's/}$//')
    
    if [ -z "$POSTGRES_PASSWORD" ]; then
        POSTGRES_PASSWORD=$(openssl rand -hex 32)
    fi
    
    if [ -z "$REDIS_PASSWORD" ]; then
        REDIS_PASSWORD=$(openssl rand -hex 32)
    fi
    
    cat > .env << EOF
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
EOF
    echo "✅ .env файл створено"
else
    echo "✅ .env файл вже існує"
fi

# Створення директорій
echo "📁 Створення директорій..."
mkdir -p nginx certbot/conf certbot/www backups
echo "✅ Директорії створено"

# Deploy
echo ""
echo "🚀 Запуск деплою..."
echo ""

# Використати deploy.sh якщо він існує
if [ -f "deploy.sh" ]; then
    chmod +x deploy.sh
    ./deploy.sh init
else
    # Ручний деплой
    echo "🔨 Будую образи..."
    docker-compose -f docker-compose.prod.yml build
    
    echo "🚀 Запускаю сервіси..."
    docker-compose -f docker-compose.prod.yml up -d
    
    echo "⏳ Чекаю готовності сервісів..."
    sleep 10
    
    echo "📊 Виконую міграції..."
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py migrate --noinput || true
    
    echo "📦 Збираю static файли..."
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py collectstatic --noinput || true
    
    echo "📋 Створюю default plans..."
    docker-compose -f docker-compose.prod.yml exec -T backend python manage.py create_default_plans || true
fi

echo ""
echo "✅ Деплой завершено!"
echo ""
echo "📊 Статус сервісів:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🔍 Перевірка:"
echo "   Health: curl https://sloth-ai.lazysoft.pl/health/"
echo "   API: curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/"
echo ""
echo "📝 Наступні кроки:"
echo "   1. Створіть суперкористувача:"
echo "      docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser"
echo "   2. Налаштуйте webhooks (Stripe, Telegram, Instagram)"
echo "   3. Перевірте логи: ./deploy.sh logs"
echo ""

