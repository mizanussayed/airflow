# Production Airflow Docker Setup

## Setup Instructions

### 1. Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your secure values
nano .env
```

### 2. Generate Secure Keys
```bash
# Generate Fernet key
python3 -c "from cryptography.fernet import Fernet; print('AIRFLOW__CORE__FERNET_KEY=' + Fernet.generate_key().decode())"

# Generate webserver secret key
python3 -c "import secrets; print('AIRFLOW__WEBSERVER__SECRET_KEY=' + secrets.token_urlsafe(32))"
```

### 3. Set Strong Passwords
Update these in your `.env` file:
- `POSTGRES_PASSWORD`: Strong database password
- `AIRFLOW_ADMIN_PASSWORD`: Strong admin password
- `AIRFLOW_ADMIN_EMAIL`: Your admin email

### 4. Production Deployment
```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## ✅ Fixed: Airflow Command Error Resolution

The original Docker Compose file had **Airflow command errors** because:

1. **Airflow 3.0.0 removed the `airflow users` command**
2. **`airflow webserver` was replaced with `airflow api-server`**
3. **Health check endpoints changed**

### What Was Fixed:

✅ **Updated commands for Airflow 3.0.0 compatibility**
- Changed `airflow webserver` → `airflow api-server`
- Removed deprecated `airflow users create` command
- Fixed health check endpoints to `/api/v2/monitor/health`

✅ **Added curl to Docker image** for health checks
✅ **Simplified user creation** - Airflow 3.0.0 auto-creates admin user
✅ **Removed unsupported Docker Compose options**
✅ **Fixed 404 health check errors**

### Login Information:

🌐 **URL**: http://localhost:8080
👤 **Username**: `admin`
🔑 **Password**: Use the password extraction script:

```bash
./get-password.sh
```

Or manually check logs:
```bash
docker-compose logs webserver | grep "Password for user"
```

The password will look like: `f234QnaM4NFBmC8x`

## Production Features

### Security Enhancements
- ✅ Environment-based secrets management
- ✅ Secure Fernet key encryption
- ✅ Strong password requirements
- ✅ Webserver secret key
- ✅ Localhost-only port binding
- ✅ Disabled example DAGs

### Reliability Improvements
- ✅ Automatic restart policies
- ✅ Resource limits and reservations
- ✅ Health checks for all services
- ✅ Proper service dependencies
- ✅ Network isolation

### Performance Optimizations
- ✅ Configurable parallelism settings
- ✅ Multiple webserver workers
- ✅ Updated PostgreSQL version
- ✅ Optimized timeout settings

## Monitoring & Maintenance

### Health Checks
```bash
# Check service health
docker-compose exec webserver airflow jobs check
docker-compose exec scheduler airflow jobs check --job-type SchedulerJob
```

### Database Backup
```bash
# Backup database
docker-compose exec postgres pg_dump -U airflow airflow > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Log Management
```bash
# View service logs
docker-compose logs webserver
docker-compose logs scheduler
docker-compose logs postgres

# Clean old logs
docker-compose exec webserver find /opt/airflow/logs -name "*.log" -mtime +7 -delete
```

## Scaling Considerations

For higher workloads, consider:
- Switching to CeleryExecutor with Redis
- Adding worker nodes
- Using external PostgreSQL database
- Implementing log persistence to external storage
- Adding monitoring (Prometheus/Grafana)

## Security Checklist

- [ ] Updated all default passwords
- [ ] Generated secure Fernet key
- [ ] Set webserver secret key
- [ ] Configured firewall rules
- [ ] Set up SSL/TLS certificates (if needed)
- [ ] Regular security updates
- [ ] Monitor access logs
