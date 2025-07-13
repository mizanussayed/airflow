# Airflow 3.0.0 Production Docker Setup

Production-ready Apache Airflow 3.0.0 deployment using Docker Compose with standalone mode.

## 🚀 Quick Start

```bash
# Deploy using the automated deployment script (recommended)
./deploy.sh

# Or start manually (ensure .env is configured first)
docker-compose up -d

# Check status
docker-compose ps

# Access Airflow UI
open http://localhost:8080

# Get admin password
./get-password.sh
```

## 📋 Prerequisites

Before deployment, ensure you have:

1. **Docker & Docker Compose installed**
2. **Environment file configured** (`.env`)
3. **Required permissions** for directory creation

The `deploy.sh` script will validate these automatically.

## 📁 Repository Structure

```
airflow-docker/
├── docker-compose.yaml              # Single production configuration
├── .env                            # Environment variables
├── deploy.sh                       # Automated deployment script
├── get-password.sh                 # Password retrieval script
├── dags/                           # Airflow DAGs
│   ├── hello_world_dag.py         # Basic test DAG
│   └── simple_test_dag.py         # Simple validation DAG
├── logs/                          # Airflow logs (auto-generated)
├── plugins/                       # Custom Airflow plugins
└── data/                         # DAG output data
```

## 🎯 Production Features

### ✅ **Working Components**
- **Airflow 3.0.0**: Latest stable version with standalone mode
- **PostgreSQL 15**: Robust metadata database
- **Standalone Mode**: All-in-one service (webserver + scheduler + executor)
- **Health Checks**: Service monitoring and auto-restart
- **Auto-restart**: Production resilience
- **Resource Limits**: 4GB RAM, 3 CPUs, optimized performance
- **Security**: Fernet encryption, secure secrets

### ✅ **Production DAGs**
- **PostgreSQL Extraction**: Extracts table metadata to JSON/CSV
- **Log Cleanup**: Automated maintenance (60-day retention)
- **Test DAGs**: Validation and debugging workflows

### ✅ **Monitoring**
- Health endpoint: `http://localhost:8080/api/v2/monitor/health`
- Resource monitoring via Docker
- Comprehensive logging

## 🛠 Environment Configuration

**⚠️ Important**: You must configure the `.env` file before deployment!

```bash
# Create your environment file (required)
cp .env.example .env

# Edit with your secure values
nano .env
```

### Required Environment Variables

The `deploy.sh` script validates these variables and will fail if not properly configured:

```bash
# Database Configuration
POSTGRES_USER=airflow
POSTGRES_PASSWORD=your_secure_db_password_here  # ⚠️ MUST CHANGE
POSTGRES_DB=airflow

# Airflow Security (all required)
AIRFLOW__CORE__FERNET_KEY=your_fernet_key_here                    # ⚠️ MUST CHANGE
AIRFLOW__WEBSERVER__SECRET_KEY=your_webserver_secret_key_here     # ⚠️ MUST CHANGE
AIRFLOW_ADMIN_PASSWORD=your_secure_admin_password_here            # ⚠️ MUST CHANGE

# Performance Tuning
AIRFLOW__CORE__PARALLELISM=64
AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG=16

# System Configuration
AIRFLOW_UID=50000
AIRFLOW_GID=0
```

### ⚠️ Security Validation

The deployment script **will not start** if any of these contain placeholder values:
- `your_secure_db_password_here`
- `your_fernet_key_here`
- `your_secure_admin_password_here`
- `your_webserver_secret_key_here`

## 📋 Deployment Process

### Automated Deployment (Recommended)

The `deploy.sh` script handles the complete deployment process:

```bash
# Run the deployment script
./deploy.sh
```

**What the script does:**
1. ✅ **Validates Prerequisites**: Checks Docker, docker-compose, and .env file
2. ✅ **Environment Validation**: Ensures all security variables are properly set
3. ✅ **Directory Setup**: Creates `dags/`, `logs/`, `plugins/`, `data/` directories
4. ✅ **Permissions**: Sets proper ownership using `AIRFLOW_UID:AIRFLOW_GID`
5. ✅ **Image Management**: Pulls latest images and stops existing containers
6. ✅ **Service Startup**: Starts Airflow in standalone mode
7. ✅ **Health Monitoring**: Waits up to 5 minutes for service to be healthy
8. ✅ **Status Report**: Displays final service status and access information

### Manual Deployment

If you prefer manual control:

```bash
# 1. Ensure .env is configured
source .env

# 2. Create directories
mkdir -p dags logs plugins data

# 3. Set permissions
sudo chown -R ${AIRFLOW_UID}:${AIRFLOW_GID} dags logs plugins data

# 4. Start services
docker-compose up -d

# 5. Check health
docker-compose ps
```

## 📋 Common Operations

### Service Management
```bash
# Full deployment (recommended)
./deploy.sh

# Quick start (after initial deployment)
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart web-server

# View service status
docker-compose ps
```
### DAG Management
```bash
# List all DAGs
docker-compose exec web-server airflow dags list

# Trigger a DAG
docker-compose exec web-server airflow dags trigger extract_table_names

# Check DAG status
docker-compose exec web-server airflow dags state <dag_id> <run_id>

# Unpause a DAG
docker-compose exec web-server airflow dags unpause cleanup_logs
```

### Health Monitoring
```bash
# Check deployment status (as done by deploy.sh)
docker-compose ps | grep web-server

# API health check
curl http://localhost:8080/api/v2/monitor/health

# View real-time logs
docker-compose logs -f web-server

# Check resource usage
docker-compose exec web-server df -h
docker-compose exec web-server free -h
```

## 🔍 Troubleshooting

### Deployment Issues

1. **Script Fails - Docker Not Running**
   ```bash
   # Error: "Docker is not running"
   sudo systemctl start docker
   # or start Docker Desktop
   ```

2. **Script Fails - Environment Validation**
   ```bash
   # Error: "Please set a secure value for AIRFLOW__CORE__FERNET_KEY"
   # Edit .env file and replace all placeholder values:
   nano .env
   # Change: your_fernet_key_here → actual_secure_key
   ```

3. **Health Check Timeout**
   ```bash
   # If deploy.sh times out waiting for health check
   docker-compose logs web-server
   
   # Common causes:
   # - Insufficient resources (increase Docker memory to 4GB+)
   # - Port 8080 already in use
   # - Database connection issues
   ```

### Runtime Issues

1. **DAG Import Errors**
   ```bash
   # Check import errors
   docker-compose exec web-server airflow dags list-import-errors
   ```

2. **Service Not Starting**
   ```bash
   # Check logs
   docker-compose logs web-server
   
   # Verify environment
   docker-compose config
   ```

3. **Database Issues**
   ```bash
   # Re-initialize database (WARNING: destroys all data)
   docker-compose down
   docker volume rm airflow-docker_postgres-db-volume
   ./deploy.sh
   ```

### Permission Issues
```bash
# If you see permission errors during deployment
sudo chown -R ${AIRFLOW_UID}:${AIRFLOW_GID} dags logs plugins data

# Or reset and redeploy
sudo rm -rf logs/* && ./deploy.sh
```

## 📊 Performance & Scaling

### Resource Optimization
- **Standalone Service**: 4GB RAM, 3 CPUs (recommended minimum)
- **Database**: 1GB RAM, 1 CPU (scales with workload)
- **Parallelism**: 64 concurrent tasks (adjust based on hardware)

### Scaling Options
1. **Vertical Scaling**: Increase resources in docker-compose.yaml
2. **Multi-Worker Setup**: Switch to CeleryExecutor with Redis
3. **External Database**: Use managed PostgreSQL for larger deployments

## 🔐 Security Best Practices

1. **Secrets Management**
   - Use strong Fernet keys
   - Rotate secrets regularly
   - Never commit secrets to Git

2. **Network Security**
   - Bind to localhost (127.0.0.1) in production
   - Use reverse proxy for external access
   - Enable HTTPS in production

3. **Access Control**
   - Admin password set via environment variable
   - Implement RBAC (Role-Based Access Control)
   - Regular security updates

## 📈 Maintenance

### Automated Tasks
- **Log Cleanup**: Runs weekly via `cleanup_logs` DAG (60-day retention)
- **Health Monitoring**: Continuous via Docker health checks
- **Auto-restart**: Services restart automatically on failure

### Manual Maintenance
```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U airflow airflow > backup.sql

# Clean up Docker resources
docker system prune -f

# Update images
docker-compose pull && docker-compose up -d
```

## 🏆 Production Checklist

- [x] Environment variables configured
- [x] Secrets generated and secured
- [x] Resource limits appropriate for workload
- [x] Health checks passing
- [x] DAGs loading without errors
- [x] Log cleanup DAG scheduled
- [x] Monitoring configured
- [x] Standalone mode deployed
- [x] Admin password configured
- [ ] Backup strategy implemented
- [ ] Security hardening applied

## 🔑 Access Information

After successful deployment with `./deploy.sh`:

🌐 **URL**: http://localhost:8080  
👤 **Username**: `admin`  
🔑 **Password**: Your `AIRFLOW_ADMIN_PASSWORD` from `.env` file

### Getting Your Password

```bash
# Method 1: Use the password script
./get-password.sh

# Method 2: Check your .env file directly
grep AIRFLOW_ADMIN_PASSWORD .env

# Method 3: View from environment
source .env && echo $AIRFLOW_ADMIN_PASSWORD
```

### First Login Steps

1. Open http://localhost:8080 in your browser
2. Use username: `admin`
3. Use password from your `.env` file
4. Navigate to **Admin → Connections** to verify PostgreSQL connection
5. Check **DAGs** page to see your workflows

---

**Status**: ✅ Production Ready | **Version**: Airflow 3.0.0 | **Mode**: Standalone | **Last Updated**: July 2025

## 💡 Development Notes

- **Standalone Mode**: All Airflow components (webserver, scheduler, executor) run in a single container
- **Auto-Created Admin**: Admin user is automatically created using environment variables
- **Health Checks**: Deployment script waits for service health before completing
- **Resource Requirements**: Minimum 4GB RAM, 3 CPUs recommended for stable operation
- **Security**: All secrets must be properly configured before deployment will succeed
