#!/bin/bash

echo "🔍 Retrieving Airflow admin password from logs..."

# Extract password from web-server logs
PASSWORD=$(docker-compose logs web-server 2>/dev/null | grep -o "Password for user 'admin': [a-zA-Z0-9]*" | head -1 | cut -d' ' -f5)

if [ -n "$PASSWORD" ]; then
    echo "✅ Admin Password Found!"
    echo ""
    echo "🌐 URL: http://localhost:8080"
    echo "👤 Username: admin"
    echo "🔑 Password: $PASSWORD"
    echo ""
    echo "💡 Tip: Copy this password to access the Airflow web interface"
    echo ""
    
    # Also check if services are running
    if docker-compose ps | grep -q "web-server.*healthy"; then
        echo "✅ Airflow web-server service is running and healthy"
    else
        echo "⚠️  Airflow service status:"
        docker-compose ps
    fi
else
    echo "❌ Password not found in logs yet."
    echo "💡 The web-server might still be starting up."
    echo "📋 Try running this script again in a few seconds, or check logs manually:"
    echo "   docker-compose logs web-server | grep -i password"
fi
