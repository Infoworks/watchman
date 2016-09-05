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
    # sys.exit(1)

args = {
    'owner': 'iw_admin',
    'start_date': datetime.now(),
    'provide_context': True,
    'depends_on_past': False,
    'schedule_interval': None
}

dag = DAG('oracle_metadata_crawl', default_args=args)


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

    crawl_table_groups_task.set_upstream(crawl_metadata_task)

create_dag()
