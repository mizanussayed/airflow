#!/bin/bash

# Production Airflow Deployment Script

set -e

echo "🚀 Starting Airflow Production Deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📋 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Source environment variables
source .env

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "AIRFLOW__CORE__FERNET_KEY" "AIRFLOW_ADMIN_PASSWORD" "AIRFLOW__WEBSERVER__SECRET_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_secure_db_password_here" ] || [ "${!var}" = "your_fernet_key_here" ] || [ "${!var}" = "your_secure_admin_password_here" ] || [ "${!var}" = "your_webserver_secret_key_here" ]; then
        echo "❌ Please set a secure value for $var in .env file"
        exit 1
    fi
done

echo "✅ Environment validation passed"

# Create required directories
echo "📁 Creating required directories..."
mkdir -p dags logs plugins

# Set proper permissions
echo "🔐 Setting permissions..."
echo "export AIRFLOW_UID=${AIRFLOW_UID}" > .env.local
sudo chown -R ${AIRFLOW_UID}:${AIRFLOW_GID} dags logs plugins

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Start services
echo "🔧 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

# Extract admin password from logs
echo "🔑 Extracting admin password..."
sleep 5
PASSWORD=$(docker-compose logs webserver 2>/dev/null | grep -o "Password for user 'admin': [a-zA-Z0-9]*" | head -1 | cut -d' ' -f5)

echo "✅ Airflow is now running!"
echo "🌐 Access the web interface at: http://localhost:8080"
echo "👤 Username: admin"
if [ -n "$PASSWORD" ]; then
    echo "🔑 Password: $PASSWORD"
else
    echo "🔑 Password: Check logs with 'docker-compose logs webserver | grep Password'"
fi
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
