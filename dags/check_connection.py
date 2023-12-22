from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import psycopg2

def test_postgres_conn():
    try:
        conn = psycopg2.connect(
            dbname="traffic_data",
            user="postgres",
            password="postgres",
            host="astro-data-warehouse_ce9b63-postgres-1",
            port="5432"
        )
        print("Connected to the database")
    except psycopg2.Error as e:
        print("Unable to connect to the database")
        print(e)

dag = DAG('test_postgres_conn', start_date=datetime(2022, 1, 1))

test_conn_task = PythonOperator(
    task_id='test_conn_task',
    python_callable=test_postgres_conn,
    dag=dag
)