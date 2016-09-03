from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from tasks.infoworks import create_source, crawl_metadata, \
    configure_tables_and_table_groups, crawl_table_groups

try:
    ROSIE_FLOW_DATASET_BASE_PATH = os.environ['ROSIE_FLOW_DATASET_BASE_PATH']
except KeyError as e:
    print 'ROSIE_FLOW_DATASET_BASE_PATH is not set as an env variable.'
    sys.exit(1)

args = {
    'owner': 'iw_admin',
    'start_date': datetime(2016, 9, 1),
    'provide_context': True,
    'depends_on_past': False
}

dag = DAG('oracle_ingestion_full_load_4', default_args=args)


def create_dag():
    """

    Flow for Oracle Northwind end to end

    """
    create_source_task = PythonOperator(
        task_id='create_source', dag=dag, python_callable=create_source,
        op_args=[ROSIE_FLOW_DATASET_BASE_PATH + '/create_source.json', None, 'source_id'])

    crawl_metadata_task = PythonOperator(
        task_id='crawl_metadata', dag=dag,
        python_callable=crawl_metadata, op_args=[None, 'create_source', 'source_id'])

    configure_tables_and_table_groups_task = PythonOperator(
        task_id='configure_tables_and_table_groups', dag=dag,
        python_callable=configure_tables_and_table_groups,
        op_args=[ROSIE_FLOW_DATASET_BASE_PATH + '/configure_tables_and_table_groups.json', None,
                 'create_source', 'source_id'])

    crawl_table_groups_task = PythonOperator(
        task_id='crawl_table_groups', dag=dag,
        python_callable=crawl_table_groups, op_args=[None, 'create_source', 'source_id'])

    crawl_metadata_task.set_upstream(create_source_task)
    configure_tables_and_table_groups_task.set_upstream(crawl_metadata_task)
    crawl_table_groups_task.set_upstream(configure_tables_and_table_groups_task)


create_dag()