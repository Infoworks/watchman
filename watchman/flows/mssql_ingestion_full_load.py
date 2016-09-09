from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os, sys, inspect
import logging
from os.path import basename
script_name = inspect.getfile(inspect.currentframe())
current_dir = os.path.dirname(os.path.abspath(script_name))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from tasks.infoworks import create_source, source_setup, crawl_metadata, \
    configure_tables_and_table_groups, crawl_table_groups_from_config, delete_source

try:
    ROSIE_FLOW_DATASET_BASE_PATH = os.environ['ROSIE_FLOW_DATASET_BASE_PATH']
except KeyError as e:
    file_name = basename(script_name).split('.')[0]
    ROSIE_FLOW_DATASET_BASE_PATH = parent_dir + '/datasets/' + file_name + '/AdventureWorks'
    logging.warn('Unable to retrieve dataset base path.')
    logging.warn('Defaulting to dataset: ' + ROSIE_FLOW_DATASET_BASE_PATH)


logging.info('Starting the flow with dataset: ' + ROSIE_FLOW_DATASET_BASE_PATH)

args = {
    'owner': 'iw_admin',
    'start_date': datetime.now(),
    'provide_context': True,
    'depends_on_past': False,
}

dag = DAG('mssql_ingestion_full_load', default_args=args, schedule_interval=None)


def create_dag():
    """

    Flow for MSSQL Ingestion end to end

    """

    create_source_task = PythonOperator(
        task_id='create_source', dag=dag, python_callable=create_source,
        op_args=[ROSIE_FLOW_DATASET_BASE_PATH + '/create_source.json','sourceID'])

    crawl_metadata_task = PythonOperator(
        task_id='crawl_metadata', dag=dag,
        python_callable=crawl_metadata, op_args=[None,'create_source','sourceID'])

    configure_tables_and_table_groups_task = PythonOperator(
        task_id='configure_tables_and_table_groups', dag=dag,
        python_callable=configure_tables_and_table_groups,
        op_args=[ROSIE_FLOW_DATASET_BASE_PATH + '/configure_tables_and_table_groups.json', None,
                 'create_source', 'sourceID'])

    crawl_table_groups_task = PythonOperator(
        task_id='crawl_table_groups', dag=dag,
        python_callable=crawl_table_groups_from_config, op_args=[ROSIE_FLOW_DATASET_BASE_PATH + '/crawl_data.json'])

    crawl_metadata_task.set_upstream(create_source_task)
    configure_tables_and_table_groups_task.set_upstream(crawl_metadata_task)
    crawl_table_groups_task.set_upstream(configure_tables_and_table_groups_task)


create_dag()
