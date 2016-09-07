from datetime import datetime
from airflow import DAG
from airflow.operators.jdbc_operator import JdbcOperator
from airflow.operators.python_operator import PythonOperator
import os,sys,inspect
from os.path import basename
script_name = inspect.getfile(inspect.currentframe())
current_dir = os.path.dirname(os.path.abspath(script_name))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from tasks.infoworks import create_source, crawl_metadata, configure_tables_and_table_groups, crawl_table_groups

try:
    ROSIE_FLOW_DATASET_BASE_PATH = os.environ['ROSIE_FLOW_DATASET_BASE_PATH']
except KeyError as e:
    file_name = basename(script_name).split('.')[0]
    print 'ROSIE_FLOW_DATASET_BASE_PATH is not set as an env variable.'
    ROSIE_FLOW_DATASET_BASE_PATH = parent_dir + '/datasets/' + file_name + '/northwind'
    print 'Defaulting to: ' + ROSIE_FLOW_DATASET_BASE_PATH

args = {
    'owner': 'iw_admin',
    'provide_context': True,
    'depends_on_past': False,
    'start_date': datetime.now()
}


dag = DAG('oracle_metadata_crawl', default_args=args, schedule_interval=None)


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
