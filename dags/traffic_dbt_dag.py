from airflow.decorators import dag
from airflow.providers.postgres.operators.postgres import PostgresOperator
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig
from cosmos.profiles import PostgresUserPasswordProfileMapping
from pendulum import datetime
import os

CONNECTION_ID = "postgres"
DB_NAME = "traffic_data"
SCHEMA_NAME = "traffic_data"
DBT_PROJECT_PATH = f"{os.environ['AIRFLOW_HOME']}/dags/dbt/traffic_dbt_project"
DBT_EXECUTABLE_PATH = f"{os.environ['AIRFLOW_HOME']}/dbt_venv/bin/dbt"

profile_config = ProfileConfig(
    profile_name="default",
    target_name="dev",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id=CONNECTION_ID,
        profile_args={"schema": SCHEMA_NAME},
    ),
)

execution_config = ExecutionConfig(
    dbt_executable_path=DBT_EXECUTABLE_PATH,
)

@dag(
    start_date=datetime(2023, 8, 1),
    schedule_interval=None,  # Set your desired schedule interval
    catchup=False,
)
def my_trajectory_summary_dbt_dag():
    with DbtTaskGroup(
        group_id="dbt_tasks",
        project_config=ProjectConfig(DBT_PROJECT_PATH),
        profile_config=profile_config,
        execution_config=execution_config,
        operator_args={},
        default_args={"retries": 2},
    ) as dbt_tasks:
        task_trajectory_summary = dbt_tasks.run_model(
            model="trajectory_summary",
            vars={},
        )

    query_trajectory_summary = PostgresOperator(
        task_id="query_trajectory_summary",
        postgres_conn_id=CONNECTION_ID,
        sql=f"SELECT * FROM {DB_NAME}.{SCHEMA_NAME}.trajectory_summary",
    )

    task_trajectory_summary >> query_trajectory_summary

my_trajectory_summary_dbt_dag()
