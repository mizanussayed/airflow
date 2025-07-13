from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import os
import json
from pathlib import Path

# DAG configuration
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 7, 12),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'extract_table_names',
    default_args=default_args,
    description='Extract table names from PostgreSQL database and save to data folder',
    schedule=timedelta(days=1),  # Run daily
    catchup=False,
    tags=['database', 'extraction', 'metadata', 'postgresql'],
)

def get_table_names(**context):
    """
    Extract table names from PostgreSQL database using Airflow connection and save to data folder
    """
    try:
        print("🔗 Connecting to PostgreSQL database using Airflow connection...")
        
        # Use Airflow PostgreSQL Hook with connection ID
        pg_hook = PostgresHook(postgres_conn_id='postgres_conn_id')
        
        print("✅ Connected successfully!")
        
        # Query to get all table names from PostgreSQL
        query = """
        SELECT 
            schemaname as table_schema,
            tablename as table_name,
            'BASE TABLE' as table_type,
            schemaname || '.' || tablename as full_name
        FROM pg_tables
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ORDER BY schemaname, tablename
        """
        
        print("📊 Executing query to get table names...")
        
        # Execute query and get results as pandas DataFrame
        df = pg_hook.get_pandas_df(sql=query)
        
        # Convert DataFrame to list of dictionaries
        tables = df.to_dict('records')
        
        print(f"🎯 Found {len(tables)} tables")
        
        # Create data directory if it doesn't exist
        data_dir = Path('/opt/airflow/data')
        data_dir.mkdir(exist_ok=True)
        
        # Save as JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_file = data_dir / f'table_names_{timestamp}.json'
        
        with open(json_file, 'w') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'database': 'medi_concern_test',
                'connection_id': 'medi_concern_postgres',
                'total_tables': len(tables),
                'tables': tables
            }, f, indent=2)
        
        print(f"💾 Saved table names to: {json_file}")
        
        # Also save as CSV for easy viewing
        csv_file = data_dir / f'table_names_{timestamp}.csv'
        df.to_csv(csv_file, index=False)
        
        print(f"📋 Saved table names to CSV: {csv_file}")
        
        # Save latest version (overwrite)
        latest_json = data_dir / 'table_names_latest.json'
        latest_csv = data_dir / 'table_names_latest.csv'
        
        with open(latest_json, 'w') as f:
            json.dump({
                'extraction_date': datetime.now().isoformat(),
                'database': 'medi_concern_test',
                'connection_id': 'medi_concern_postgres',
                'total_tables': len(tables),
                'tables': tables
            }, f, indent=2)
        
        df.to_csv(latest_csv, index=False)
        
        print(f"📌 Updated latest files: {latest_json}, {latest_csv}")
        
        # Log some sample table names
        print("📋 Sample tables found:")
        for i, table in enumerate(tables[:10]):  # Show first 10 tables
            print(f"  {i+1}. {table['full_name']}")
        
        if len(tables) > 10:
            print(f"  ... and {len(tables) - 10} more tables")
        
        print("🔐 Database connection closed")
        
        return {
            'total_tables': len(tables),
            'extraction_date': datetime.now().isoformat(),
            'files_created': [str(json_file), str(csv_file)]
        }
        
    except Exception as e:
        print(f"❌ Error extracting table names: {str(e)}")
        raise e

def validate_extraction(**context):
    """
    Validate that the extraction was successful
    """
    ti = context['ti']
    result = ti.xcom_pull(task_ids='extract_tables')
    
    if result and result['total_tables'] > 0:
        print(f"✅ Validation successful: {result['total_tables']} tables extracted")
        print(f"📅 Extraction date: {result['extraction_date']}")
        
        # Check if files exist
        data_dir = Path('/opt/airflow/data')
        latest_json = data_dir / 'table_names_latest.json'
        latest_csv = data_dir / 'table_names_latest.csv'
        
        if latest_json.exists() and latest_csv.exists():
            print("✅ All output files exist")
            
            # Print file sizes
            json_size = latest_json.stat().st_size
            csv_size = latest_csv.stat().st_size
            print(f"📊 File sizes - JSON: {json_size} bytes, CSV: {csv_size} bytes")
        else:
            raise Exception("❌ Output files missing")
            
    else:
        raise Exception("❌ No tables were extracted")

# Define tasks
extract_tables_task = PythonOperator(
    task_id='extract_tables',
    python_callable=get_table_names,
    dag=dag,
)

validate_task = PythonOperator(
    task_id='validate_extraction',
    python_callable=validate_extraction,
    dag=dag,
)

# Set task dependencies
extract_tables_task >> validate_task
