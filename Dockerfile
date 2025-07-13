FROM apache/airflow:3.0.0

# Switch to root to install packages
USER root

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy user creation script
COPY create_user.py /opt/airflow/create_user.py
RUN chmod +x /opt/airflow/create_user.py

# Switch back to airflow user
USER airflow

# Install Python packages for PostgreSQL connectivity
RUN pip install --no-cache-dir psycopg2-binary pandas apache-airflow-providers-postgres
