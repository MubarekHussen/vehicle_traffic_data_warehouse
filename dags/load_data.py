from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 12, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('load_data_to_postgres',
          default_args=default_args,
          description='A DAG to load data into PostgreSQL',
          schedule='@daily',
          catchup=False
        )

def read_csv_to_df(file_path):
    return pd.read_csv(file_path)

def write_df_to_postgres(df, table_name, engine):
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Data written to {table_name} successfully.")

def load_data(file_path, table_name, engine):
    df = read_csv_to_df(file_path)
    df.columns = df.columns.str.strip()
    if df.empty:
        print(f"No data in {table_name} DataFrame.")
    else:
        print(f"Data is available in {table_name} DataFrame.")
        print(df.head())

    write_df_to_postgres(df, table_name, engine)

file_paths = ['/usr/local/airflow/include/dataset/trajectory_data.csv',
              '/usr/local/airflow/include/dataset/vehicle_positions_data.csv']
table_names = ['trajectory_info', 'vehicle_positions']

engine = create_engine('postgresql+psycopg2://postgres:postgres@astro-data-warehouse_ce9b63-postgres-1:5432/traffic_data')

load_trajectory_data = PythonOperator(
    task_id='load_trajectory_data',
    python_callable=load_data,
    op_kwargs={'file_path': file_paths[0], 'table_name': table_names[0], 'engine': engine},
    dag=dag,
)

load_vehicle_positions_data = PythonOperator(
    task_id='load_vehicle_positions_data',
    python_callable=load_data,
    op_kwargs={'file_path': file_paths[1], 'table_name': table_names[1], 'engine': engine},
    dag=dag,
)

load_trajectory_data >> load_vehicle_positions_data