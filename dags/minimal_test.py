from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator

# Ultra-minimal configuration
dag = DAG(
    'minimal_test',
    start_date=datetime(2025, 7, 13),
    schedule=None,
    catchup=False,
    tags=['minimal'],
)

def minimal_function():
    """Absolute minimal function"""
    print("✅ Minimal task executed successfully")
    return "success"

# Single task
PythonOperator(
    task_id='minimal_task',
    python_callable=minimal_function,
    dag=dag,
)
