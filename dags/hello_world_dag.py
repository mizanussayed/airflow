from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

# DAG configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

dag = DAG(
    'hello_world_test',
    default_args=default_args,
    description='Simple test DAG to verify Airflow scheduler is working',
    schedule=timedelta(minutes=5),  # Run every 5 minutes for testing
    catchup=False,
    tags=['test', 'hello-world', 'scheduler-test'],
)

def say_hello(**context):
    """
    Simple Python function to test DAG execution
    """
    current_time = datetime.now().isoformat()
    print(f"🎉 Hello from Airflow! Current time: {current_time}")
    print(f"📅 Execution date: {context['ds']}")
    print(f"🔧 Task ID: {context['task_instance'].task_id}")
    print(f"🏷️ DAG ID: {context['dag'].dag_id}")
    
    # Return some data for downstream tasks
    return {
        'message': 'Hello World!',
        'execution_time': current_time,
        'status': 'success'
    }

def validate_hello(**context):
    """
    Validate the hello task completed successfully
    """
    ti = context['ti']
    result = ti.xcom_pull(task_ids='say_hello')
    
    if result and result.get('status') == 'success':
        print(f"✅ Hello task validation successful!")
        print(f"💬 Message received: {result['message']}")
        print(f"⏰ Execution time: {result['execution_time']}")
    else:
        raise Exception("❌ Hello task validation failed")

# Define tasks
hello_task = PythonOperator(
    task_id='say_hello',
    python_callable=say_hello,
    dag=dag,
)

# Simple bash task
date_task = BashOperator(
    task_id='print_date',
    bash_command='echo "Current date and time: $(date)"',
    dag=dag,
)

# Validation task
validate_task = PythonOperator(
    task_id='validate_hello',
    python_callable=validate_hello,
    dag=dag,
)

# Another simple task
system_info_task = BashOperator(
    task_id='system_info',
    bash_command='''
    echo "🖥️ System Information:"
    echo "Hostname: $(hostname)"
    echo "User: $(whoami)"
    echo "Working directory: $(pwd)"
    echo "Python version: $(python --version)"
    echo "Airflow location: $(which airflow)"
    ''',
    dag=dag,
)

# Set task dependencies
hello_task >> [date_task, validate_task]
date_task >> system_info_task
validate_task >> system_info_task
