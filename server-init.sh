#!/bin/bash

# Sloth AI - Automated Server Setup Script
# For Hetzner CPX31 (128.140.65.237)
# Domain: sloth-ai.lazysoft.pl

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_step() {
    echo -e "${BLUE}==>${NC} $1"
}

echo_success() {
    echo -e "${GREEN}✓${NC} $1"
}

echo_error() {
    echo -e "${RED}✗${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}!${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo_error "Please run as root (use: sudo bash server-init.sh)"
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║         Sloth AI - Server Setup Script              ║"
echo "║         Hetzner CPX31 - sloth-ai.lazysoft.pl        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Step 1: System Update
echo_step "Step 1/10: Updating system packages..."
apt update -qq
apt upgrade -y -qq
echo_success "System updated"

# Step 2: Install essential packages
echo_step "Step 2/10: Installing essential packages..."
apt install -y -qq curl wget git vim htop ufw python3 python3-pip
echo_success "Essential packages installed"

# Step 3: Install Docker
echo_step "Step 3/10: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    echo_success "Docker installed"
else
    echo_success "Docker already installed"
fi

# Step 4: Install Docker Compose
echo_step "Step 4/10: Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    apt install -y -qq docker-compose-plugin
    echo_success "Docker Compose installed"
else
    echo_success "Docker Compose already installed"
fi

# Verify Docker installation
DOCKER_VERSION=$(docker --version | awk '{print $3}')
COMPOSE_VERSION=$(docker compose version | awk '{print $4}')
echo "  Docker: $DOCKER_VERSION"
echo "  Compose: $COMPOSE_VERSION"

# Step 5: Configure Firewall
echo_step "Step 5/10: Configuring firewall (UFW)..."
ufw --force reset > /dev/null 2>&1
ufw default deny incoming > /dev/null 2>&1
ufw default allow outgoing > /dev/null 2>&1
ufw allow 22/tcp > /dev/null 2>&1   # SSH
ufw allow 80/tcp > /dev/null 2>&1   # HTTP
ufw allow 443/tcp > /dev/null 2>&1  # HTTPS
ufw --force enable > /dev/null 2>&1
echo_success "Firewall configured"
echo "  Ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)"

# Step 6: Create deployment directory
echo_step "Step 6/10: Creating deployment directory..."
mkdir -p /var/www
cd /var/www
echo_success "Directory created: /var/www"

# Step 7: Clone repository
echo_step "Step 7/10: Cloning Sloth AI repository..."
if [ -d "/var/www/sloth" ]; then
    echo_warn "Repository already exists, pulling latest changes..."
    cd sloth
    git pull origin main
else
    git clone https://github.com/ChuprinaDaria/sloth.git
    cd sloth
    echo_success "Repository cloned"
fi

# Step 8: Create necessary directories
echo_step "Step 8/10: Creating application directories..."
mkdir -p nginx certbot/conf certbot/www backups
chmod +x deploy.sh 2>/dev/null || true
echo_success "Directories created"

# Step 9: Configure environment files
echo_step "Step 9/10: Setting up environment files..."

if [ ! -f "backend/.env.production" ]; then
    cp backend/.env.production.example backend/.env.production
    echo_warn "Created backend/.env.production - CONFIGURE IT BEFORE DEPLOYMENT!"
else
    echo_success "backend/.env.production already exists"
fi

if [ ! -f ".env.production" ]; then
    cp .env.production.example .env.production
    echo_warn "Created .env.production - CONFIGURE IT BEFORE DEPLOYMENT!"
else
    echo_success ".env.production already exists"
fi

# Generate random passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
DJANGO_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')

# Create .env file for docker-compose
cat > .env << EOF
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
EOF

echo_success "Generated secure passwords"
echo ""
echo "  📝 Save these credentials securely:"
echo "  ├─ PostgreSQL Password: $POSTGRES_PASSWORD"
echo "  ├─ Redis Password: $REDIS_PASSWORD"
echo "  └─ Django Secret Key: $DJANGO_SECRET"
echo ""

# Update backend/.env.production with generated values
if grep -q "CHANGE_DB_PASSWORD" backend/.env.production; then
    sed -i "s/CHANGE_DB_PASSWORD/$POSTGRES_PASSWORD/g" backend/.env.production
    sed -i "s/redis_password/$REDIS_PASSWORD/g" backend/.env.production
    sed -i "s/CHANGE_THIS_TO_RANDOM_SECRET_KEY_IN_PRODUCTION/$DJANGO_SECRET/g" backend/.env.production
    echo_success "Updated environment files with generated credentials"
fi

# Step 10: Summary and next steps
echo_step "Step 10/10: Installation complete!"
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              ✓ Server Setup Complete!               ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo_success "System is ready for Sloth AI deployment"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Configure API keys in environment files:"
echo "   nano /var/www/sloth/backend/.env.production"
echo ""
echo "   Required API keys:"
echo "   ├─ OPENAI_API_KEY=sk-..."
echo "   ├─ STRIPE_SECRET_KEY=sk_live_..."
echo "   ├─ STRIPE_PUBLISHABLE_KEY=pk_live_..."
echo "   ├─ GOOGLE_CLIENT_ID=..."
echo "   ├─ GOOGLE_CLIENT_SECRET=..."
echo "   ├─ FACEBOOK_APP_ID=..."
echo "   └─ FACEBOOK_APP_SECRET=..."
echo ""
echo "2️⃣  Configure frontend environment:"
echo "   nano /var/www/sloth/.env.production"
echo ""
echo "   Update:"
echo "   └─ VITE_STRIPE_PUBLIC_KEY=pk_live_..."
echo ""
echo "3️⃣  Obtain SSL certificates:"
echo "   cd /var/www/sloth"
echo "   docker run -it --rm \\"
echo "     -v \$(pwd)/certbot/conf:/etc/letsencrypt \\"
echo "     -v \$(pwd)/certbot/www:/var/www/certbot \\"
echo "     certbot/certbot certonly --webroot \\"
echo "     --webroot-path=/var/www/certbot \\"
echo "     --email your-email@lazysoft.pl \\"
echo "     --agree-tos -d sloth-ai.lazysoft.pl"
echo ""
echo "4️⃣  Deploy application:"
echo "   cd /var/www/sloth"
echo "   ./deploy.sh init"
echo ""
echo "5️⃣  Create admin user:"
echo "   docker-compose -f docker-compose.prod.yml exec backend \\"
echo "     python manage.py createsuperuser"
echo ""
echo "6️⃣  Configure webhooks:"
echo "   └─ Stripe: https://sloth-ai.lazysoft.pl/webhooks/stripe/"
echo ""
echo "📖 Full documentation: /var/www/sloth/SERVER_SETUP.md"
echo ""
echo "🌐 Your domains:"
echo "   ├─ https://sloth-ai.lazysoft.pl (will be available after SSL + deploy)"
echo "   └─ IP: 128.140.65.237"
echo ""
echo "✨ Setup completed successfully!"
echo ""
