from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os, sys, inspect
from os.path import basename
script_name = inspect.getfile(inspect.currentframe())
current_dir = os.path.dirname(os.path.abspath(script_name))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import DAG_DEFAULT_CONFIG
from tasks.infoworks import create_source,source_setup, crawl_metadata, \
    configure_tables_and_table_groups, crawl_table_groups_from_config, delete_source


dag = DAG('rdbms_end_to_end_query_based_cdc', default_args=DAG_DEFAULT_CONFIG, schedule_interval=None)


def create_dag():
    """

    Flow for Oracle Northwind end to end

    """
    delete_source_task = PythonOperator(
        task_id='delete_source', dag=dag,
        python_callable=delete_source, op_args=['/delete_source.json'])

    source_setup_task = PythonOperator(
        task_id='setup_source', dag=dag, python_callable=source_setup,
        op_args=['/dbconf.properties', '/fullload.sql'])

    create_source_task = PythonOperator(
        task_id='create_source', dag=dag, python_callable=create_source,
        op_args=['/create_source.json','sourceID'])

    crawl_metadata_task = PythonOperator(
        task_id='crawl_metadata', dag=dag,
        python_callable=crawl_metadata, op_args=[None,'create_source','sourceID'])

    configure_tables_and_table_groups_task = PythonOperator(
        task_id='configure_tables_and_table_groups', dag=dag,
        python_callable=configure_tables_and_table_groups,
        op_args=['/configure_tables_and_table_groups.json', None, 'create_source', 'sourceID'])

    full_load_task = PythonOperator(
        task_id='crawl_table_groups', dag=dag,
        python_callable=crawl_table_groups_from_config, op_args=['/full_load.json'])

    cdc_setup_task = PythonOperator(
        task_id='setup_cdc', dag=dag, python_callable=source_setup,
        op_args=['/dbconf.properties', '/cdc.sql'])

    cdc_merge_task = PythonOperator(
        task_id='cdc_merge', dag=dag,
        python_callable=crawl_table_groups_from_config, op_args=['/cdc.json'])

    source_setup_task.set_upstream(delete_source_task)
    create_source_task.set_upstream(source_setup_task)
    crawl_metadata_task.set_upstream(create_source_task)
    configure_tables_and_table_groups_task.set_upstream(crawl_metadata_task)
    full_load_task.set_upstream(configure_tables_and_table_groups_task)
    cdc_setup_task.set_upstream(full_load_task)
    cdc_merge_task.set_upstream(cdc_setup_task)


create_dag()
