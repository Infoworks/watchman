from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os,sys,inspect
from os.path import basename
script_name = inspect.getfile(inspect.currentframe())
current_dir = os.path.dirname(os.path.abspath(script_name))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import DAG_DEFAULT_CONFIG
from tasks.infoworks import create_source, crawl_metadata, configure_tables_and_table_groups, crawl_table_groups


dag = DAG('oracle_metadata_crawl', default_args=DAG_DEFAULT_CONFIG, schedule_interval=None)


def create_dag():
    """
    Flow for Oracle Northwind end to end
    """
    crawl_metadata_task = PythonOperator(
        task_id='crawl_metadata', dag=dag,
        python_callable=crawl_metadata, op_args=['be87a5bdb6c687d8b0980f01', None, None])

    crawl_table_groups_task = PythonOperator(
        task_id='crawl_table_groups', dag=dag,
        python_callable=crawl_table_groups, op_args=['be87a5bdb6c687d8b0980f01', None, None])


create_dag()
