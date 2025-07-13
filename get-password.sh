#!/bin/bash

# Get Airflow Admin Password Script

echo "🔍 Retrieving Airflow admin password..."

# Extract password from webserver logs
PASSWORD=$(docker-compose logs webserver 2>/dev/null | grep -o "Password for user 'admin': [a-zA-Z0-9]*" | head -1 | cut -d' ' -f5)

if [ -n "$PASSWORD" ]; then
    echo "✅ Admin Password Found!"
    echo ""
    echo "🌐 URL: http://localhost:8080"
    echo "👤 Username: admin"
    echo "🔑 Password: $PASSWORD"
    echo ""
    echo "💡 Tip: Copy this password to access the Airflow web interface"
else
    echo "❌ Password not found in logs yet."
    echo "💡 The webserver might still be starting up."
    echo "📋 Try running this script again in a few seconds, or check logs manually:"
    echo "   docker-compose logs webserver | grep -i password"
fi
