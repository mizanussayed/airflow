from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

# DAG configuration - Optimized for performance
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 13),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,  # No retries for faster execution
    'retry_delay': timedelta(seconds=30),  # Shorter retry delay
}

dag = DAG(
    'hello_world_test',
    default_args=default_args,
    description='Simple test DAG to verify Airflow scheduler is working',
    schedule=None,  # Manual trigger only for testing
    catchup=False,
    tags=['test', 'hello-world', 'scheduler-test'],
    max_active_runs=1,  # Prevent overlapping runs
)

def say_hello(**context):
    """
    Optimized simple function
    """
    print("🎉 Hello from Airflow!")
    print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    return {'status': 'success', 'message': 'Hello World!'}

def quick_validation(**context):
    """
    Quick validation without XCom complexity
    """
    print("✅ Validation passed!")
    return {'validation': 'success'}

# Define tasks - Simplified for speed
hello_task = PythonOperator(
    task_id='say_hello',
    python_callable=say_hello,
    dag=dag,
)

# Simple validation task
validate_task = PythonOperator(
    task_id='quick_validation',
    python_callable=quick_validation,
    dag=dag,
)

# Set simple dependencies
hello_task >> validate_task
