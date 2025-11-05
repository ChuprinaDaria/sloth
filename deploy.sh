#!/bin/bash

# Sloth AI - Production Deployment Script
# Usage: ./deploy.sh [init|update|restart|backup]

set -e  # Exit on error

COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_DIR="/var/www/sloth"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_env_file() {
    if [ ! -f "backend/.env.production" ]; then
        echo_error "backend/.env.production not found!"
        echo_info "Copy backend/.env.production.example and configure it"
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo_error "Docker is not installed!"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo_error "Docker Compose is not installed!"
        exit 1
    fi
}

init_deployment() {
    echo_info "Initializing Sloth AI deployment..."

    check_docker
    check_env_file

    # Create necessary directories
    echo_info "Creating directories..."
    mkdir -p nginx certbot/conf certbot/www

    # Build and start services
    echo_info "Building and starting services..."
    docker-compose -f $COMPOSE_FILE up -d --build

    # Wait for services to be ready
    echo_info "Waiting for services to be ready..."
    sleep 10

    # Run migrations
    echo_info "Running database migrations..."
    docker-compose -f $COMPOSE_FILE exec -T backend python manage.py migrate --noinput

    # Collect static files
    echo_info "Collecting static files..."
    docker-compose -f $COMPOSE_FILE exec -T backend python manage.py collectstatic --noinput

    # Create default plans
    echo_info "Creating default subscription plans..."
    docker-compose -f $COMPOSE_FILE exec -T backend python manage.py create_default_plans || true

    echo_info "Deployment initialized successfully!"
    echo_warn "Remember to:"
    echo "  1. Create superuser: docker-compose -f $COMPOSE_FILE exec backend python manage.py createsuperuser"
    echo "  2. Set up SSL certificates (see DEPLOYMENT.md)"
    echo "  3. Configure webhooks for Stripe, Telegram, etc."
}

update_deployment() {
    echo_info "Updating Sloth AI deployment..."

    check_docker
    check_env_file

    # Pull latest code
    echo_info "Pulling latest code..."
    git pull origin main

    # Backup database
    echo_info "Creating database backup..."
    backup_database

    # Build and restart services
    echo_info "Rebuilding services..."
    docker-compose -f $COMPOSE_FILE up -d --build

    # Wait for services
    echo_info "Waiting for services..."
    sleep 5

    # Run migrations
    echo_info "Running migrations..."
    docker-compose -f $COMPOSE_FILE exec -T backend python manage.py migrate --noinput

    # Collect static files
    echo_info "Collecting static files..."
    docker-compose -f $COMPOSE_FILE exec -T backend python manage.py collectstatic --noinput

    echo_info "Update completed successfully!"
}

restart_services() {
    echo_info "Restarting services..."

    docker-compose -f $COMPOSE_FILE restart

    echo_info "Services restarted!"
}

backup_database() {
    BACKUP_DIR="backups"
    mkdir -p $BACKUP_DIR

    BACKUP_FILE="$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sql"

    echo_info "Creating database backup: $BACKUP_FILE"
    docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U sloth sloth > $BACKUP_FILE

    # Compress
    gzip $BACKUP_FILE

    echo_info "Backup created: ${BACKUP_FILE}.gz"

    # Keep only last 7 backups
    ls -t $BACKUP_DIR/db_backup_*.sql.gz | tail -n +8 | xargs -r rm
}

backup_media() {
    BACKUP_DIR="backups"
    mkdir -p $BACKUP_DIR

    BACKUP_FILE="$BACKUP_DIR/media_backup_$(date +%Y%m%d_%H%M%S).tar.gz"

    echo_info "Creating media backup: $BACKUP_FILE"
    docker run --rm -v sloth_media_volume:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/$(basename $BACKUP_FILE) /data

    echo_info "Backup created: $BACKUP_FILE"
}

view_logs() {
    echo_info "Viewing logs (Ctrl+C to exit)..."
    docker-compose -f $COMPOSE_FILE logs -f --tail=100
}

show_status() {
    echo_info "Service Status:"
    docker-compose -f $COMPOSE_FILE ps

    echo ""
    echo_info "Health Checks:"

    # Check nginx
    if curl -f -s https://sloth-ai.lazysoft.pl/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend is accessible"
    else
        echo -e "${RED}✗${NC} Frontend is not accessible"
    fi

    # Check API
    if curl -f -s https://sloth-ai.lazysoft.pl/api/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} API is accessible"
    else
        echo -e "${RED}✗${NC} API is not accessible"
    fi

    # Check health endpoint
    if curl -f -s https://sloth-ai.lazysoft.pl/health/ > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Health check passed"
    else
        echo -e "${RED}✗${NC} Health check failed"
    fi
}

# Main script
case "${1:-}" in
    init)
        init_deployment
        ;;
    update)
        update_deployment
        ;;
    restart)
        restart_services
        ;;
    backup)
        backup_database
        backup_media
        ;;
    logs)
        view_logs
        ;;
    status)
        show_status
        ;;
    *)
        echo "Sloth AI - Deployment Script"
        echo ""
        echo "Usage: $0 {init|update|restart|backup|logs|status}"
        echo ""
        echo "Commands:"
        echo "  init     - Initial deployment (first time)"
        echo "  update   - Update deployment with latest code"
        echo "  restart  - Restart all services"
        echo "  backup   - Backup database and media files"
        echo "  logs     - View logs (real-time)"
        echo "  status   - Show service status and health"
        echo ""
        exit 1
        ;;
esac
