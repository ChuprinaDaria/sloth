#!/bin/bash

# Script to apply Django migrations in the backend container

echo "Applying Django migrations..."

# Try with docker compose (new syntax)
if command -v docker &> /dev/null; then
    if docker compose version &> /dev/null; then
        echo "Using 'docker compose' command..."
        docker compose exec backend python manage.py migrate
    elif docker-compose version &> /dev/null; then
        echo "Using 'docker-compose' command..."
        docker-compose exec backend python manage.py migrate
    else
        echo "Error: Neither 'docker compose' nor 'docker-compose' is available"
        exit 1
    fi
else
    echo "Error: Docker is not available"
    exit 1
fi

echo "Migrations applied successfully!"
