# Sloth AI - Hetzner CPX31 Server Setup Guide

## 🖥️ Server Specifications

**Hetzner Cloud - CPX31 #109707184**
- **Name:** LazysoftWEB
- **IPv4:** 128.140.65.237
- **IPv6:** 2a01:4f8:1c1a:b28f::/64
- **CPU:** 4 vCPU
- **RAM:** 8 GB
- **Disk:** 80 GB SSD
- **Traffic:** 20 TB/month
- **Price:** €16.11/month
- **Location:** Germany (eu-central)

## ✅ DNS Configuration (DONE)

```
A | sloth-ai.lazysoft.pl | 128.140.65.237 | 3600
```

## 🚀 Initial Server Setup

### 1. Connect to Server

```bash
ssh root@128.140.65.237
```

### 2. Update System

```bash
apt update && apt upgrade -y
apt install -y curl wget git vim htop
```

### 3. Install Docker & Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

### 4. Configure Firewall (UFW)

```bash
# Install UFW
apt install -y ufw

# Allow SSH (IMPORTANT! Do this first)
ufw allow 22/tcp

# Allow HTTP and HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

**Expected output:**
```
Status: active

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW       Anywhere
80/tcp                     ALLOW       Anywhere
443/tcp                     ALLOW       Anywhere
```

### 5. Create Deploy User (Optional, but recommended)

```bash
# Create user
adduser deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Test (logout and login as deploy)
su - deploy
docker ps
```

### 6. Clone Repository

```bash
# Create directory
mkdir -p /var/www
cd /var/www

# Clone project
git clone https://github.com/ChuprinaDaria/sloth.git
cd sloth

# Checkout production branch (if different from main)
git checkout main
```

### 7. Configure Environment Files

```bash
cd /var/www/sloth

# Backend configuration
cp backend/.env.production.example backend/.env.production
nano backend/.env.production
```

**Required environment variables to set:**

```bash
# Django
SECRET_KEY=GENERATE_RANDOM_SECRET_KEY_HERE
DEBUG=False
ALLOWED_HOSTS=sloth-ai.lazysoft.pl,lazysoft.pl,www.lazysoft.pl

# Database (change password!)
POSTGRES_PASSWORD=your_secure_database_password_here

# Redis (change password!)
REDIS_PASSWORD=your_secure_redis_password_here

# OpenAI
OPENAI_API_KEY=sk-proj-your-openai-api-key

# Stripe
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_public_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Google OAuth (for Calendar + Sheets)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Facebook/Instagram
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
FACEBOOK_WEBHOOK_VERIFY_TOKEN=your_random_verification_token

# Email (Gmail example)
EMAIL_HOST_USER=noreply@lazysoft.pl
EMAIL_HOST_PASSWORD=your_gmail_app_password

# Sentry (optional)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# URLs
BACKEND_URL=https://sloth-ai.lazysoft.pl
FRONTEND_URL=https://sloth-ai.lazysoft.pl
```

**Frontend configuration:**

```bash
cp .env.production.example .env.production
nano .env.production
```

```bash
VITE_API_URL=https://sloth-ai.lazysoft.pl/api
VITE_STRIPE_PUBLIC_KEY=pk_live_your_stripe_public_key
VITE_ENV=production
```

### 8. Generate Secret Key

```bash
# Generate Django SECRET_KEY
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Or use openssl
openssl rand -base64 50
```

### 9. Set Environment Variables for Docker

```bash
# Create .env file for docker-compose
cat > .env << 'EOF'
POSTGRES_PASSWORD=your_secure_database_password
REDIS_PASSWORD=your_secure_redis_password
EOF
```

### 10. Obtain SSL Certificates (Let's Encrypt)

**First, create directories:**

```bash
mkdir -p nginx certbot/conf certbot/www
```

**Get certificates:**

```bash
# Test with staging first (to avoid rate limits)
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email \
  --staging \
  -d sloth-ai.lazysoft.pl

# If successful, get production certificates
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos \
  --no-eff-email \
  -d sloth-ai.lazysoft.pl
```

### 11. Deploy Application

```bash
cd /var/www/sloth

# Make deploy script executable
chmod +x deploy.sh

# Initial deployment
./deploy.sh init
```

**This will:**
1. Build all Docker images
2. Start all services
3. Run database migrations
4. Collect static files
5. Create default subscription plans

### 12. Create Django Superuser

```bash
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py createsuperuser
```

Enter:
- Username: `admin`
- Email: `admin@lazysoft.pl`
- Password: (your secure password)

### 13. Verify Deployment

```bash
# Check all services are running
docker-compose -f docker-compose.prod.yml ps

# Check logs
./deploy.sh logs

# Check status
./deploy.sh status
```

**Test endpoints:**

```bash
# Health check
curl https://sloth-ai.lazysoft.pl/health/

# API
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Frontend
curl https://sloth-ai.lazysoft.pl/
```

**Visit in browser:**
- https://sloth-ai.lazysoft.pl/ - Landing page
- https://sloth-ai.lazysoft.pl/admin/ - Django admin
- https://sloth-ai.lazysoft.pl/register/ - Registration

## 🔧 Post-Deployment Configuration

### Configure Stripe Webhooks

1. Go to: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://sloth-ai.lazysoft.pl/webhooks/stripe/`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the signing secret to `STRIPE_WEBHOOK_SECRET` in `.env.production`

### Configure Telegram Bot Webhooks

For each organization's bot:

```bash
curl -F "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/<org_id>/" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

### Configure Instagram Webhooks

1. Go to: https://developers.facebook.com/
2. Select your app
3. Products → Webhooks
4. Callback URL: `https://sloth-ai.lazysoft.pl/webhooks/instagram/`
5. Verify Token: (from `FACEBOOK_WEBHOOK_VERIFY_TOKEN`)
6. Subscribe to: `messages`, `messaging_postbacks`

## 📊 Monitoring

### View Logs

```bash
# All services
./deploy.sh logs

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f celery
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Check Service Status

```bash
./deploy.sh status
```

### Celery Flower (Task Monitoring)

Access via SSH tunnel:

```bash
# On your local machine
ssh -L 5555:localhost:5555 root@128.140.65.237

# Then open in browser
http://localhost:5555
```

## 🔄 Maintenance

### Update Application

```bash
cd /var/www/sloth
./deploy.sh update
```

### Restart Services

```bash
./deploy.sh restart
```

### Backup Database

```bash
./deploy.sh backup
```

Backups are stored in `backups/` directory.

### Manual Database Backup

```bash
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U sloth sloth > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database

```bash
cat backup_YYYYMMDD_HHMMSS.sql | \
  docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U sloth sloth
```

## 🔒 Security Checklist

- [x] Firewall enabled (UFW)
- [x] Only ports 22, 80, 443 open
- [x] SSL certificates installed (Let's Encrypt)
- [x] DEBUG=False
- [x] Strong SECRET_KEY generated
- [x] Database password changed
- [x] Redis password set
- [x] CORS configured for production domains
- [x] Security headers enabled (HSTS, etc.)
- [x] Sentry error tracking configured
- [ ] SSH key-based authentication (disable password login)
- [ ] Regular backups automated
- [ ] Monitoring set up

### Disable SSH Password Login (Recommended)

```bash
# Generate SSH key on your local machine (if not exists)
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key to server
ssh-copy-id root@128.140.65.237

# On server, disable password authentication
nano /etc/ssh/sshd_config

# Change these lines:
PasswordAuthentication no
PermitRootLogin prohibit-password

# Restart SSH
systemctl restart sshd
```

## 📈 Resource Monitoring

### Check disk space

```bash
df -h
```

### Check memory usage

```bash
free -h
```

### Check Docker stats

```bash
docker stats
```

### Clean up Docker

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune
```

## 🆘 Troubleshooting

### Service won't start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps postgres

# Check DATABASE_URL in .env.production
# Make sure password matches POSTGRES_PASSWORD
```

### SSL certificate issues

```bash
# Check certificate
docker-compose -f docker-compose.prod.yml exec nginx \
  ls -la /etc/letsencrypt/live/sloth-ai.lazysoft.pl/

# Renew certificate
docker-compose -f docker-compose.prod.yml exec certbot certbot renew

# Reload nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### 502 Bad Gateway

```bash
# Check backend is running
docker-compose -f docker-compose.prod.yml ps backend

# Check backend logs
docker-compose -f docker-compose.prod.yml logs backend

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

## 📞 Support

- **Server:** Hetzner CPX31 #109707184
- **IP:** 128.140.65.237
- **Domain:** sloth-ai.lazysoft.pl
- **Email:** support@lazysoft.pl

---

**Deployment completed! 🎉**

Visit: https://sloth-ai.lazysoft.pl
