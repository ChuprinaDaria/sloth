# Sloth AI - Quick Start Guide 🦥

## Production Deployment (sloth-ai.lazysoft.pl)

### 🚀 One-Command Deploy

```bash
# 1. Clone repository
git clone https://github.com/ChuprinaDaria/sloth.git
cd sloth

# 2. Configure environment
cp backend/.env.production.example backend/.env.production
nano backend/.env.production  # Edit with your keys

# 3. Deploy!
chmod +x deploy.sh
./deploy.sh init
```

### 📋 What You Need

1. **Server:** Ubuntu/Debian with Docker
2. **Domain:** Point `sloth-ai.lazysoft.pl` to your server IP
3. **API Keys:**
   - OpenAI API key
   - Stripe keys (secret + publishable)
   - Google OAuth credentials
   - Facebook App credentials

### ⚙️ Configuration Files

**Backend:** `backend/.env.production`
```bash
SECRET_KEY=generate-random-secret-key
DEBUG=False
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl

OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

FACEBOOK_APP_ID=...
FACEBOOK_APP_SECRET=...
```

**Frontend:** `.env.production`
```bash
VITE_API_URL=https://sloth-ai.lazysoft.pl/api
VITE_STRIPE_PUBLIC_KEY=pk_live_...
VITE_ENV=production
```

### 🔒 SSL Certificates (Let's Encrypt)

```bash
# Install certbot and get certificates
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  -d sloth-ai.lazysoft.pl
```

### 🎯 Deployment Commands

```bash
# Initial deployment
./deploy.sh init

# Update (pull latest code + rebuild)
./deploy.sh update

# Restart services
./deploy.sh restart

# Backup database & media
./deploy.sh backup

# View logs
./deploy.sh logs

# Check status
./deploy.sh status
```

### ✅ Post-Deployment Checklist

- [ ] Create admin user: `docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser`
- [ ] Visit https://sloth-ai.lazysoft.pl and verify landing page loads
- [ ] Test registration flow
- [ ] Configure Stripe webhooks: `https://sloth-ai.lazysoft.pl/webhooks/stripe/`
- [ ] Set up Telegram bot webhook
- [ ] Configure Instagram webhook in Meta console

### 🔍 Health Checks

```bash
# Frontend
curl https://sloth-ai.lazysoft.pl/

# API
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Health endpoint
curl https://sloth-ai.lazysoft.pl/health/
```

### 📊 Monitoring

- **Logs:** `./deploy.sh logs`
- **Status:** `./deploy.sh status`
- **Sentry:** https://sentry.io (configure SENTRY_DSN)

### 🆘 Troubleshooting

**502 Bad Gateway:**
```bash
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml restart backend
```

**Database errors:**
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

**Static files not loading:**
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### 📚 Full Documentation

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

**Need help?**
- 📧 Email: support@lazysoft.pl
- 🐛 Issues: https://github.com/ChuprinaDaria/sloth/issues
