# Sloth AI - Quick Server Commands

## 🖥️ Server Info
- **IP:** 128.140.65.237
- **Domain:** sloth-ai.lazysoft.pl
- **Server:** Hetzner CPX31 (4 vCPU, 8GB RAM, 80GB SSD)

## 🔐 Connect to Server

```bash
ssh root@128.140.65.237
```

## 🚀 Quick Setup (First Time)

```bash
# 1. Copy setup script to server
scp server-init.sh root@128.140.65.237:/root/

# 2. SSH to server
ssh root@128.140.65.237

# 3. Run setup script
bash server-init.sh

# 4. Configure .env files
cd /var/www/sloth
nano backend/.env.production
nano .env.production

# 5. Get SSL certificate
docker run -it --rm \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  -v $(pwd)/certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@lazysoft.pl \
  --agree-tos -d sloth-ai.lazysoft.pl

# 6. Deploy
./deploy.sh init

# 7. Create admin
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py createsuperuser
```

## 🔄 Daily Operations

### Deploy/Update

```bash
cd /var/www/sloth

# Update to latest code
./deploy.sh update

# Restart all services
./deploy.sh restart

# View logs (live)
./deploy.sh logs

# Check status
./deploy.sh status
```

### Backup

```bash
cd /var/www/sloth

# Backup everything (DB + media)
./deploy.sh backup

# Manual DB backup
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U sloth sloth > backup_$(date +%Y%m%d_%H%M%S).sql
```

### View Logs

```bash
cd /var/www/sloth

# All services
docker-compose -f docker-compose.prod.yml logs -f

# Backend only
docker-compose -f docker-compose.prod.yml logs -f backend

# Nginx only
docker-compose -f docker-compose.prod.yml logs -f nginx

# Celery worker
docker-compose -f docker-compose.prod.yml logs -f celery

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Service Management

```bash
cd /var/www/sloth

# Restart specific service
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart nginx
docker-compose -f docker-compose.prod.yml restart celery

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Django Management

```bash
cd /var/www/sloth

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py collectstatic --noinput

# Create superuser
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py createsuperuser

# Django shell
docker-compose -f docker-compose.prod.yml exec backend \
  python manage.py shell

# Database shell
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U sloth sloth
```

## 🔍 Monitoring

### Check Service Status

```bash
# Docker services
docker-compose -f docker-compose.prod.yml ps

# System resources
htop

# Disk space
df -h

# Memory
free -h

# Docker stats (real-time)
docker stats
```

### Test Endpoints

```bash
# Health check
curl https://sloth-ai.lazysoft.pl/health/

# API
curl https://sloth-ai.lazysoft.pl/api/subscriptions/plans/

# Frontend
curl -I https://sloth-ai.lazysoft.pl/

# Admin
curl -I https://sloth-ai.lazysoft.pl/admin/
```

### SSL Certificate

```bash
# Check expiry
docker-compose -f docker-compose.prod.yml exec certbot \
  certbot certificates

# Renew certificate
docker-compose -f docker-compose.prod.yml exec certbot \
  certbot renew

# Test renewal (dry run)
docker-compose -f docker-compose.prod.yml exec certbot \
  certbot renew --dry-run
```

## 🔒 Security

### Firewall

```bash
# Check status
ufw status

# Allow new port
ufw allow 8080/tcp

# Deny port
ufw deny 8080/tcp

# Reload firewall
ufw reload
```

### Update System

```bash
# Update packages
apt update && apt upgrade -y

# Reboot (if kernel updated)
reboot
```

## 🧹 Cleanup

### Docker Cleanup

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused containers
docker container prune

# Full cleanup (BE CAREFUL!)
docker system prune -a --volumes
```

### Disk Space

```bash
# Check what's using space
du -sh /var/www/sloth/*
du -sh /var/lib/docker/*

# Clean old backups (keep last 7 days)
find /var/www/sloth/backups -name "*.sql.gz" -mtime +7 -delete
```

## 🆘 Troubleshooting

### Backend not responding

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs backend

# Restart
docker-compose -f docker-compose.prod.yml restart backend

# Check if running
docker-compose -f docker-compose.prod.yml ps backend
```

### 502 Bad Gateway

```bash
# Check nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Check backend is running
docker-compose -f docker-compose.prod.yml ps

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Database errors

```bash
# Check postgres
docker-compose -f docker-compose.prod.yml ps postgres

# View postgres logs
docker-compose -f docker-compose.prod.yml logs postgres

# Access database
docker-compose -f docker-compose.prod.yml exec postgres \
  psql -U sloth sloth
```

### Out of disk space

```bash
# Check space
df -h

# Clean Docker
docker system prune -a

# Remove old logs
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Restart Docker
systemctl restart docker
```

## 📊 Performance Monitoring

### Check CPU/Memory

```bash
# Real-time monitoring
htop

# Per container
docker stats

# Server load
uptime
```

### Celery Monitoring (Flower)

```bash
# Access via SSH tunnel (from local machine)
ssh -L 5555:localhost:5555 root@128.140.65.237

# Then open: http://localhost:5555
```

## 🔄 Git Operations

```bash
cd /var/www/sloth

# Pull latest code
git pull origin main

# Check current branch
git branch

# View recent commits
git log --oneline -10

# Stash local changes
git stash

# Apply stashed changes
git stash pop
```

## 📦 Environment Variables

```bash
# Edit backend env
nano /var/www/sloth/backend/.env.production

# Edit frontend env
nano /var/www/sloth/.env.production

# After changing, restart:
docker-compose -f docker-compose.prod.yml restart backend
```

## 🎯 Quick Health Check

```bash
# One-liner to check everything
curl -s https://sloth-ai.lazysoft.pl/health/ && \
  echo "✓ Frontend OK" || echo "✗ Frontend DOWN"

curl -s https://sloth-ai.lazysoft.pl/api/ && \
  echo "✓ API OK" || echo "✗ API DOWN"
```

## 📞 Webhooks Setup

### Stripe

Dashboard: https://dashboard.stripe.com/webhooks
Endpoint: `https://sloth-ai.lazysoft.pl/webhooks/stripe/`

### Telegram

```bash
curl -F "url=https://sloth-ai.lazysoft.pl/webhooks/telegram/<org_id>/" \
     https://api.telegram.org/bot<BOT_TOKEN>/setWebhook
```

### Instagram

Meta Console: https://developers.facebook.com/
Callback: `https://sloth-ai.lazysoft.pl/webhooks/instagram/`

---

**Server:** Hetzner CPX31 #109707184
**IP:** 128.140.65.237
**Domain:** sloth-ai.lazysoft.pl
