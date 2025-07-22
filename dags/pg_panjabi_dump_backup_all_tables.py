from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pathlib import Path
import subprocess
import os
import gzip
import shutil

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'pg_panjabiDb_dump_backup_gz',
    default_args=default_args,
    description='Full PostgreSQL backup compressed as .sql.gz with cleanup of old backups',
    schedule=timedelta(days=1),
    catchup=False,
    tags=['backup', 'postgresql', 'pg_dump', 'gzip'],
)

# Paths
BACKUP_ROOT = Path("/opt/airflow/data/backups_sql")
RETENTION_DAYS = 7

def run_full_pg_dump(**context):
    print("🔌 Getting DB connection info...")
    pg_hook = PostgresHook(postgres_conn_id='panjabi_postgres_conn_id')
    conn = pg_hook.get_connection(pg_hook.postgres_conn_id)

    host = conn.host
    port = conn.port or 5432
    user = conn.login
    password = conn.password
    database = conn.schema

    # Create timestamped backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = BACKUP_ROOT / f"backup_panjabi_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Define raw and compressed output files
    raw_file = backup_dir / f"{database}_full_backup.sql"
    gz_file = backup_dir / f"{database}_full_backup.sql.gz"

    print(f"💾 Starting pg_dump to: {raw_file}")

    try:
        subprocess.run(
            [
                "pg_dump",
                "-h", host,
                "-p", str(port),
                "-U", user,
                "-d", database,
                "-f", str(raw_file)
            ],
            check=True,
            env={**os.environ, 'PGPASSWORD': password},
            timeout=600  # 10 minutes max
        )
        print(f"✅ pg_dump completed: {raw_file}")

        # Compress the .sql file
        print(f"📦 Compressing to: {gz_file}")
        with open(raw_file, 'rb') as f_in:
            with gzip.open(gz_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove uncompressed file
        raw_file.unlink()
        print(f"🧹 Removed uncompressed file: {raw_file}")

        return {
            'backup_dir': str(backup_dir),
            'backup_file': str(gz_file),
            'timestamp': timestamp
        }

    except subprocess.TimeoutExpired:
        raise Exception("⏱ Timeout occurred during pg_dump")
    except subprocess.CalledProcessError as e:
        raise Exception(f"❌ pg_dump failed: {e}")

def cleanup_old_backups(**context):
    """
    Delete backup folders older than RETENTION_DAYS
    """
    now = datetime.now()
    deleted = []

    for path in BACKUP_ROOT.glob("backup_*"):
        try:
            # Extract timestamp
            folder_time = datetime.strptime(path.name.replace("backup_", ""), "%Y%m%d_%H%M%S")
            age_days = (now - folder_time).days
            if age_days > RETENTION_DAYS:
                shutil.rmtree(path)
                deleted.append(str(path))
                print(f"🗑 Deleted old backup: {path}")
        except Exception as e:
            print(f"⚠ Skipped {path} due to error: {e}")

    if not deleted:
        print("✅ No old backups to clean.")
    else:
        print(f"🧹 Cleaned up {len(deleted)} old backups.")

# Tasks
run_backup = PythonOperator(
    task_id='run_full_pg_dump',
    python_callable=run_full_pg_dump,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_backups',
    python_callable=cleanup_old_backups,
    dag=dag,
)

# Set task dependencies
run_backup >> cleanup_task
