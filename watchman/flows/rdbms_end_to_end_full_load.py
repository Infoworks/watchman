from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os, sys, inspect

script_name = inspect.getfile(inspect.currentframe())
current_dir = os.path.dirname(os.path.abspath(script_name))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import DAG_DEFAULT_CONFIG
from tasks.infoworks import create_source, crawl_metadata, \
    configure_tables_and_table_groups, crawl_table_groups_from_config, delete_source


dag = DAG('oracle_ingestion_full_load', default_args=DAG_DEFAULT_CONFIG, schedule_interval=None)


def create_dag():
    """

    Flow for Oracle Ingestion end to end

    """
    delete_source_task = PythonOperator(
        task_id='delete_source', dag=dag,
        python_callable=delete_source, op_args=['/delete_source.json'])

    create_source_task = PythonOperator(
        task_id='create_source', dag=dag, python_callable=create_source,
        op_args=['/create_source.json', 'source_id'])

    crawl_metadata_task = PythonOperator(
        task_id='crawl_metadata', dag=dag,
        python_callable=crawl_metadata, op_args=['/crawl_metadata.json'])

    configure_tables_and_table_groups_task = PythonOperator(
        task_id='configure_tables_and_table_groups', dag=dag,
        python_callable=configure_tables_and_table_groups,
        op_args=['/configure_tables_and_table_groups.json', None,
                 'create_source', 'source_id'])

    crawl_table_groups_task = PythonOperator(
        task_id='crawl_table_groups', dag=dag,
        python_callable=crawl_table_groups_from_config, op_args=['/crawl_data.json'])

    create_source_task.set_upstream(delete_source_task)
    crawl_metadata_task.set_upstream(create_source_task)
    configure_tables_and_table_groups_task.set_upstream(crawl_metadata_task)
    crawl_table_groups_task.set_upstream(configure_tables_and_table_groups_task)

create_dag()
