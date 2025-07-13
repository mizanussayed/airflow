"""
DAG to clean up Airflow log files older than 60 days
This DAG helps maintain disk space by removing old log files automatically.
"""

from datetime import datetime, timedelta
import os
import logging
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 13),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'cleanup_logs',
    default_args=default_args,
    description='Clean up Airflow log files older than 60 days',
    schedule='0 2 * * 0',  # Run weekly on Sunday at 2 AM
    start_date=datetime(2025, 7, 13),
    catchup=False,
    max_active_runs=1,
    tags=['maintenance', 'cleanup', 'logs'],
)

def cleanup_old_logs(**context):
    """
    Remove log files older than 60 days from the Airflow logs directory
    """
    logs_dir = '/opt/airflow/logs'
    days_to_keep = 60
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    
    deleted_count = 0
    deleted_size = 0
    
    try:
        logging.info(f"Starting log cleanup for files older than {days_to_keep} days")
        logging.info(f"Cutoff date: {cutoff_date}")
        logging.info(f"Scanning directory: {logs_dir}")
        
        # Walk through all directories and files in logs
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Check if file is older than cutoff date
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_count += 1
                        deleted_size += file_size
                        logging.info(f"Deleted: {file_path} (modified: {file_mtime})")
                        
                except OSError as e:
                    logging.warning(f"Could not process file {file_path}: {e}")
                    continue
        
        # Convert bytes to MB for better readability
        deleted_size_mb = deleted_size / (1024 * 1024)
        
        logging.info(f"Cleanup completed!")
        logging.info(f"Files deleted: {deleted_count}")
        logging.info(f"Space freed: {deleted_size_mb:.2f} MB")
        
        # Store results in XCom for next task
        return {
            'deleted_count': deleted_count,
            'deleted_size_mb': round(deleted_size_mb, 2),
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error during log cleanup: {e}")
        raise

def cleanup_empty_directories(**context):
    """
    Remove empty directories after log cleanup
    """
    logs_dir = '/opt/airflow/logs'
    removed_dirs = 0
    
    try:
        logging.info("Starting cleanup of empty directories")
        
        # Walk through directories bottom-up to remove empty ones
        for root, dirs, files in os.walk(logs_dir, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    # Check if directory is empty
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        removed_dirs += 1
                        logging.info(f"Removed empty directory: {dir_path}")
                except OSError as e:
                    logging.warning(f"Could not remove directory {dir_path}: {e}")
                    continue
        
        logging.info(f"Empty directory cleanup completed!")
        logging.info(f"Directories removed: {removed_dirs}")
        
        return {'removed_directories': removed_dirs}
        
    except Exception as e:
        logging.error(f"Error during directory cleanup: {e}")
        raise

def generate_cleanup_report(**context):
    """
    Generate a summary report of the cleanup operation
    """
    # Get results from previous tasks
    cleanup_results = context['task_instance'].xcom_pull(task_ids='cleanup_old_log_files')
    directory_results = context['task_instance'].xcom_pull(task_ids='cleanup_empty_directories')
    
    report = f"""
LOG CLEANUP REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
==================================================
Files deleted: {cleanup_results.get('deleted_count', 0)}
Space freed: {cleanup_results.get('deleted_size_mb', 0)} MB
Empty directories removed: {directory_results.get('removed_directories', 0)}
Cutoff date: {cleanup_results.get('cutoff_date', 'N/A')}
==================================================
    """
    
    logging.info(report)
    print(report)
    
    return report

# Task to check disk space before cleanup
check_disk_space = BashOperator(
    task_id='check_disk_space_before',
    bash_command="""
    echo "=== DISK SPACE BEFORE CLEANUP ==="
    df -h /opt/airflow/logs
    echo "=== LOG DIRECTORY SIZE ==="
    du -sh /opt/airflow/logs
    echo "=== LOG FILE COUNT ==="
    find /opt/airflow/logs -type f | wc -l
    """,
    dag=dag,
)

# Task to clean up old log files
cleanup_logs_task = PythonOperator(
    task_id='cleanup_old_log_files',
    python_callable=cleanup_old_logs,
    dag=dag,
)

# Task to remove empty directories
cleanup_dirs_task = PythonOperator(
    task_id='cleanup_empty_directories',
    python_callable=cleanup_empty_directories,
    dag=dag,
)

# Task to check disk space after cleanup
check_disk_space_after = BashOperator(
    task_id='check_disk_space_after',
    bash_command="""
    echo "=== DISK SPACE AFTER CLEANUP ==="
    df -h /opt/airflow/logs
    echo "=== LOG DIRECTORY SIZE ==="
    du -sh /opt/airflow/logs
    echo "=== LOG FILE COUNT ==="
    find /opt/airflow/logs -type f | wc -l
    """,
    dag=dag,
)

# Task to generate summary report
report_task = PythonOperator(
    task_id='generate_cleanup_report',
    python_callable=generate_cleanup_report,
    dag=dag,
)

# Define task dependencies
check_disk_space >> cleanup_logs_task >> cleanup_dirs_task >> check_disk_space_after >> report_task
