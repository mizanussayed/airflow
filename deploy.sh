#!/bin/bash

# Production Airflow Deployment Script - Web Server Mode

set -e

echo "🚀 Starting Airflow Production Deployment (Web Server Mode)..."

# Extract admin password from logs
echo "🔑 Extracting admin password from logs..."
sleep 5
PASSWORD=$(docker-compose logs web-server 2>/dev/null | grep -o "Password for user 'admin': [a-zA-Z0-9]*" | head -1 | cut -d' ' -f5)

echo ""
echo "✅ Airflow is now running with web-server!"
echo "🌐 Access the web interface at: http://localhost:8080"
echo "👤 Username: admin"
if [ -n "$PASSWORD" ]; then
    echo "🔑 Password: $PASSWORD"
else
    echo "🔑 Password: Check logs with 'docker-compose logs web-server | grep Password'"
fi
echo ""
echo "📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
echo "� Note: Using standalone mode - all Airflow components run in web-server container"📊 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
echo "💡 Note: Using standalone mode - all Airflow components run in web-server container"Airflow Production Deployment (Standalone Mode)..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📋 Please create a .env file with your configuration."
    exit 1
fi

# Source environment variables
source .env

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "AIRFLOW__CORE__FERNET_KEY" "AIRFLOW__WEBSERVER__SECRET_KEY")

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ] || [ "${!var}" = "your_secure_db_password_here" ] || [ "${!var}" = "your_fernet_key_here" ] || [ "${!var}" = "your_webserver_secret_key_here" ]; then
        echo "❌ Please set a secure value for $var in .env file"
        exit 1
    fi
done

echo "✅ Environment validation passed"

# Create required directories
echo "📁 Creating required directories..."
mkdir -p dags logs plugins data

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R ${AIRFLOW_UID}:${AIRFLOW_GID} dags logs plugins data

# Pull latest images
echo "📥 Pulling latest Docker images..."
docker-compose pull

# Stop any running containers
echo "🛑 Stopping any running containers..."
docker-compose down

# Start services
echo "🔧 Starting Airflow services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for Airflow web-server to be ready..."
sleep 15

# Check if standalone service is healthy
echo "🔍 Checking service health..."
for i in {1..30}; do
    if docker-compose ps | grep -q "web-server.*healthy"; then
        echo "✅ Airflow web-server service is healthy!"
        break
    elif [ $i -eq 30 ]; then
        echo "❌ Airflow health check timed out"
        echo "📋 Service status:"
        docker-compose ps
        exit 1
    else
        echo "⏳ Waiting for Airflow to be healthy... ($i/30)"
        sleep 10
    fi
done

# Check service status
echo "🔍 Final service status:"
docker-compose ps

echo ""
echo "✅ Airflow is now running with web-server!"
echo "🌐 Access the web interface at: http://localhost:8080"
echo "👤 Username: admin"
echo "🔑 Password: Set in your .env file (AIRFLOW_ADMIN_PASSWORD)"
echo ""
echo "� To view logs: docker-compose logs -f"
echo "� To stop: docker-compose down"
echo ""
echo "� Note: Using standalone mode - all Airflow components run in a single container"
