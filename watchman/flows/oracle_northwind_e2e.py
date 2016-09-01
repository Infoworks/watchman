from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from tasks.infoworks import create_source, submit_source_metadata_crawl_job, \
                                     create_table_group, submit_all_table_groups_crawl_job

args = {
    'owner': 'iw_admin',
    'start_date': datetime(2016, 9, 1),
    'provide_context': True
}

dag = DAG('workflow_18', default_args=args)

source_name = 'TEST_SOURCE_01_09_8'
source_config = '{"configuration":{"name":"' + source_name + '","hive_schema":"' + source_name + '","hdfs_path":"/iw/sources/' + source_name + '","sourceType":"rdbms","sourceSubtype": "oracle", "connection":{"connection_string":"jdbc:oracle:thin:@52.5.131.69:1521:xe","username":"northwind","password":"IN11**rk","schema":"NORTHWIND","database":"ORACLE","driver_name":"oracle.jdbc.driver.OracleDriver"},"cdc_mode":"full-load"}}'
table_group_config = '{"entity":{"entity_type":"source","entity_id":{"$type":"oid","$value":"733c2472c29eb20b7465ab31"},"entity_name":"Source_Oracle_Northwind_testing"},"source":{"connection":{"connection_string":"jdbc:oracle:thin:@52.5.131.69:1521:xe","username":"northwind","password":"SU4xMSoqcms=","schema":"NORTHWIND","database":"ORACLE","driver_name":"oracle.jdbc.driver.OracleDriver"},"cdc_mode":"full-load","hive_schema":"Source_Oracle_Northwind_testing","sourceType":"rdbms"},"tables":[{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69c3"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"CATEGORIES","chunk_load":{"status":"disabled","column":{}},"natural_key":["CATEGORY_ID"],"partition_key_derive_function":"","offset_cdc_start":0,"partition_key_extract_from_col":false,"offset_cdc_end":0,"schema_synchronization_enabled":false,"split_by_key_derive_function":"","split_by_key":"CATEGORY_ID","partition_value_changeable":false,"query_insert":"","query_update":"","split_by_key_extract_from_col":false,"export_enabled":false}}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69c8"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"CUSTOMERS","chunk_load":{"status":"enabled","column":{"sqlType":12,"name":"CITY"},"extract_from_col":false},"natural_key":[],"partition_key_derive_function":"","offset_cdc_start":0,"partition_key_extract_from_col":false,"offset_cdc_end":0,"schema_synchronization_enabled":false,"split_by_key_derive_function":"","partition_value_changeable":false,"query_insert":"","query_update":"","split_by_key_extract_from_col":false,"export_enabled":false}}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69cd"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"EMPLOYEES","natural_key":["EMPLOYEE_ID"],"partition_key_derive_function":"","offset_cdc_start":0,"partition_key_extract_from_col":false,"offset_cdc_end":0,"schema_synchronization_enabled":false,"split_by_key_derive_function":"","partition_value_changeable":false,"query_insert":"","query_update":"","split_by_key_extract_from_col":false,"export_enabled":false}}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69d2"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"ORDERS","chunk_load":{"status":"disabled","column":{}},"natural_key":["ORDER_ID","CUSTOMER_ID","EMPLOYEE_ID"],"partition_key_derive_function":"year-month","number_of_reducers":2,"offset_cdc_start":0,"partition_key_extract_from_col":true,"offset_cdc_end":0,"schema_synchronization_enabled":false,"partition_key_derive_column":"req_year_month","split_by_key_derive_column":"shipped_year","split_by_key_derive_function":"year","partition_key":["REQUIRED_DATE"],"split_by_key":"SHIPPED_DATE","partition_value_changeable":false,"number_of_secondary_partitions":1,"query_insert":"","query_update":"","split_by_key_extract_from_col":true,"export_enabled":false}}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69d7"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"ORDER_DETAILS"}}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69dc"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"PRODUCTS"}}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69e1"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"SHIPPERS","chunk_load":{"status":"disabled","column":{}},"natural_key":[],"partition_key_derive_function":"","offset_cdc_start":0,"partition_key_extract_from_col":false,"offset_cdc_end":0,"schema_synchronization_enabled":false,"split_by_key_derive_function":"","partition_key":["COMPANY_NAME"],"partition_value_changeable":false,"query_insert":"","query_update":"","split_by_key_extract_from_col":false,"export_enabled":false}}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69e6"},"configuration":{"configuration":{"sync_type":"full-load","hive_table_name":"SUPPLIERS"}}}],"table_groups":[{"entity_type":"table_group","entity_id":{"$type":"oid","$value":"cbff3158a7cc5eb22f73babb"},"configuration":{"tables":[{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69e1"},{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69c3"},{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69cd"},{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69d2"}],"name":"test_oracle_group","merge_schedule":{},"source":{"$type":"oid","$value":"733c2472c29eb20b7465ab31"},"cdc_schedule":{},"combined_schedule":{},"scheduling":"none","data_expiry_schedule":{"schedule_status":"disabled"},"fullload_schedule":{}}}],"iw_mappings":[{"entity_type":"source","entity_id":{"$type":"oid","$value":"733c2472c29eb20b7465ab31"},"recommendation":{"source_name":"Source_Oracle_Northwind_testing"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69c3"},"recommendation":{"table_name":"CATEGORIES"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69c8"},"recommendation":{"table_name":"CUSTOMERS"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69cd"},"recommendation":{"table_name":"EMPLOYEES"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69d2"},"recommendation":{"table_name":"ORDERS"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69d7"},"recommendation":{"table_name":"ORDER_DETAILS"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69dc"},"recommendation":{"table_name":"PRODUCTS"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69e1"},"recommendation":{"table_name":"SHIPPERS"}},{"entity_type":"table","entity_id":{"$type":"oid","$value":"575e5d89e4b0aa9d40bf69e6"},"recommendation":{"table_name":"SUPPLIERS"}},{"entity_type":"table_group","entity_id":{"$type":"oid","$value":"cbff3158a7cc5eb22f73babb"},"recommendation":{"table_group_name":"test_oracle_group"}}],"export":{"exportedAt":{"$date":1472720296583},"exportedBy":"Infoworks Admin"}}'
table_config = ''
source_id = None


def create_dag():
    """
    Flow for Oracle Northwind end to end
    """
    create_source_task = PythonOperator(
        task_id='create_source_task', dag=dag, python_callable=create_source, op_args=[source_config])

    crawl_metadata_task = PythonOperator(
        task_id='crawl_metadata_task', dag=dag,
        python_callable=submit_source_metadata_crawl_job, op_args=[None, 'create_source_task'])

    create_table_group_task = PythonOperator(
        task_id='create_table_group_task', dag=dag,
        python_callable=create_table_group, op_args=[table_group_config])

    submit_all_table_groups_crawl_task = PythonOperator(
        task_id='submit_all_table_groups_crawl_task', dag=dag,
        python_callable=submit_all_table_groups_crawl_job, op_args=[None, 'create_source_task'])

    crawl_metadata_task.set_upstream(create_source_task)
    create_table_group_task.set_upstream(crawl_metadata_task)
    submit_all_table_groups_crawl_task.set_upstream(create_table_group_task)


create_dag()
