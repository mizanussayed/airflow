#!/bin/bash

# Setup PostgreSQL Connection in Airflow

echo "🔧 Setting up PostgreSQL connection in Airflow..."

# Connection details from your connection string
HOST="medi-concern-htechbd22-9cc7.e.aivencloud.com"
PORT="12475"
DATABASE="medi_concern_test"
USERNAME="avnadmin"
PASSWORD=""
CONN_ID="medi_concern_postgres"

echo "📊 Connection details:"
echo "  Host: $HOST"
echo "  Port: $PORT"
echo "  Database: $DATABASE"
echo "  Username: $USERNAME"
echo "  Connection ID: $CONN_ID"

# Wait for Airflow to be ready
echo "⏳ Waiting for Airflow webserver to be ready..."
sleep 10

# Create the connection using Airflow CLI
echo "🔗 Creating PostgreSQL connection..."

docker-compose exec webserver airflow connections create \
    "$CONN_ID" \
    --conn-type "postgres" \
    --conn-host "$HOST" \
    --conn-port "$PORT" \
    --conn-login "$USERNAME" \
    --conn-password "$PASSWORD" \
    --conn-schema "$DATABASE"

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL connection created successfully!"
    echo ""
    echo "🎯 You can now run the DAG 'extract_table_names'"
    echo "📋 The DAG will:"
    echo "   - Connect to your PostgreSQL database"
    echo "   - Extract all table names"
    echo "   - Save results to ./data/ folder"
    echo ""
    echo "🚀 Access Airflow UI: http://localhost:8080"
    echo "👀 Find your DAG: extract_table_names"
else
    echo "❌ Failed to create connection. Please check if Airflow is running."
    echo "💡 You can also create the connection manually via the Airflow UI:"
    echo "   1. Go to Admin > Connections"
    echo "   2. Click '+' to add new connection"
    echo "   3. Use the details shown above"
fi
