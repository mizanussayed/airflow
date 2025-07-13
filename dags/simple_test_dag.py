from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

# Minimal DAG configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 13),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,  # No retries for testing
}

dag = DAG(
    'simple_test',
    default_args=default_args,
    description='Ultra-simple test DAG',
    schedule=None,  # Manual trigger only
    catchup=False,
    tags=['test', 'simple'],
    max_active_runs=1,
)

def simple_task(**context):
    """
    Ultra-simple task that just prints and returns
    """
    import time
    start_time = time.time()
    
    print("🚀 Starting simple task...")
    print(f"⏰ Task started at: {datetime.now().isoformat()}")
    
    # Simulate some work
    time.sleep(2)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Simple task completed in {duration:.2f} seconds")
    print(f"⏰ Task finished at: {datetime.now().isoformat()}")
    
    return {
        'status': 'success',
        'duration': duration,
        'message': 'Simple task completed successfully'
    }

# Single task
simple_task_op = PythonOperator(
    task_id='simple_task',
    python_callable=simple_task,
    dag=dag,
)

# No dependencies - just one task
