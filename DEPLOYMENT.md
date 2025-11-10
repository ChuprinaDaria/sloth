# Sloth AI - Production Deployment Guide
## Domain: sloth-ai.lazysoft.pl

## Prerequisites

1. **Server Requirements:**
   - Ubuntu 20.04+ / Debian 11+
   - 4GB RAM minimum (8GB recommended)
   - 40GB+ disk space
   - Docker & Docker Compose installed

2. **Domain Setup:**
   - DNS A record: `sloth-ai.lazysoft.pl` → Server IP
   - DNS A record: `lazysoft.pl` → Server IP (optional)
   - DNS A record: `www.lazysoft.pl` → Server IP (optional)

3. **Required Accounts:**
   - OpenAI API key
   - Stripe account (for payments)
   - Google Cloud (for OAuth, Vision API)
   - Facebook Developer (for Instagram integration)
   - Email service (Gmail/SendGrid)

## Initial Setup

### 1. Clone Repository

```bash
cd /var/www
git clone https://github.com/ChuprinaDaria/sloth.git
cd sloth
git checkout main  # or your production branch
```

### 2. Configure Environment Variables

#### Backend Configuration

```bash
cd backend
cp .env.production.example .env.production
nano .env.production
```

**Important variables to set:**
```bash
# Generate a secure SECRET_KEY
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Generate FERNET_KEY for encrypting integration credentials (REQUIRED!)
FERNET_KEY=$(python3 -c "import base64; import os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())")
# Or use: python backend/generate_fernet_key.py

# Database password
POSTGRES_PASSWORD=your_secure_db_password

# OpenAI (REQUIRED for AI features)
OPENAI_API_KEY=sk-...

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# Facebook/Instagram
FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
FACEBOOK_WEBHOOK_VERIFY_TOKEN=your_random_token

# Email (Gmail example)
EMAIL_HOST_USER=noreply@lazysoft.pl
EMAIL_HOST_PASSWORD=your_app_password

# Sentry (optional but recommended)
SENTRY_DSN=https://...@sentry.io/...
```

#### Frontend Configuration

```bash
cd /var/www/sloth
cp .env.production .env.production.local
nano .env.production.local
```

Update Stripe public key:
```bash
VITE_STRIPE_PUBLIC_KEY=pk_live_...
```

### 3. SSL Certificates (Let's Encrypt)

First, create nginx directory structure:
```bash
mkdir -p nginx certbot/conf certbot/www
```

Initial certificate creation (use staging for testing):
```bash
# Staging (testing)
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email \
  --staging \
  -d sloth-ai.lazysoft.pl \
  -d lazysoft.pl \
  -d www.lazysoft.pl

# Production (after testing)
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email \
  -d sloth-ai.lazysoft.pl \
  -d lazysoft.pl \
  -d www.lazysoft.pl
```

## Deployment

### 1. Build and Start Services

```bash
# Set passwords as environment variables
export POSTGRES_PASSWORD=your_secure_db_password
export REDIS_PASSWORD=your_secure_redis_password

# Build and start
docker-compose -f docker-compose.prod.yml up -d --build
```

### 2. Initialize Database

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

# Create default subscription plans
docker-compose -f docker-compose.prod.yml exec backend python manage.py create_default_plans
```

### 3. Verify Deployment

Check all services are running:
```bash
docker-compose -f docker-compose.prod.yml ps
```

Check logs:
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f nginx
```

Test endpoints:
```bash
# Health check
curl https://sloth-ai.lazysoft.pl/health/

# API
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Frontend
curl https://sloth-ai.lazysoft.pl/
```

## Post-Deployment Configuration

### 1. Stripe Webhooks

Add webhook endpoint in Stripe Dashboard:
- URL: `https://sloth-ai.lazysoft.pl/webhooks/stripe/`
- Events: `checkout.session.completed`, `customer.subscription.updated`, etc.

### 2. Telegram Bot Webhook

For each bot:
```bash
curl -F "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/<bot_id>/" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

### 3. WhatsApp/Instagram Webhooks

Configure in Meta Developer Console:
- Callback URL: `https://sloth-ai.lazysoft.pl/webhooks/instagram/`
- Verify Token: (from FACEBOOK_WEBHOOK_VERIFY_TOKEN)

## Maintenance

### Updates

```bash
cd /var/www/sloth
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### Backups

Database backup:
```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U sloth sloth > backup_$(date +%Y%m%d_%H%M%S).sql
```

Media files backup:
```bash
docker run --rm -v sloth_media_volume:/data -v $(pwd):/backup alpine tar czf /backup/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

### Logs

View logs:
```bash
# Recent logs
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# Follow logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Restart Services

```bash
# All services
docker-compose -f docker-compose.prod.yml restart

# Specific service
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart celery
```

## Monitoring

### Health Checks

- Frontend: https://sloth-ai.lazysoft.pl/
- Backend API: https://sloth-ai.lazysoft.pl/api/
- Admin: https://sloth-ai.lazysoft.pl/admin/
- Health: https://sloth-ai.lazysoft.pl/health/

### Celery Monitoring (Flower)

Access Flower at: http://server-ip:5555 (internal only, use SSH tunnel)

```bash
ssh -L 5555:localhost:5555 user@server-ip
```

### Sentry

Monitor errors at: https://sentry.io/organizations/your-org/issues/

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check backend is running: `docker-compose -f docker-compose.prod.yml ps backend`
   - Check logs: `docker-compose -f docker-compose.prod.yml logs backend`

2. **Database connection errors**
   - Verify postgres is healthy: `docker-compose -f docker-compose.prod.yml ps postgres`
   - Check DATABASE_URL in .env.production

3. **SSL Certificate issues**
   - Renew manually: `docker-compose -f docker-compose.prod.yml exec certbot certbot renew`
   - Check nginx config: `docker-compose -f docker-compose.prod.yml exec nginx nginx -t`

4. **Static files not loading**
   - Run collectstatic: `docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput`

## Security Checklist

- [ ] Changed all default passwords
- [ ] Generated new SECRET_KEY
- [ ] SSL certificates installed and auto-renewing
- [ ] DEBUG=False in production
- [ ] Sentry configured for error tracking
- [ ] Database backups automated
- [ ] Firewall configured (only 80, 443, 22)
- [ ] SSH key-based authentication only
- [ ] All API keys secured in .env.production (not committed to git)

## Support

For issues or questions:
- Email: support@lazysoft.pl
- GitHub Issues: https://github.com/ChuprinaDaria/sloth/issues
