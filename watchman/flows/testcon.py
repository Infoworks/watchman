# from datetime import datetime
# from airflow import DAG
# from airflow.operators.jdbc_operator import JdbcOperator
# import os, sys, inspect
#
# args = {
#     'owner': 'iw_admin',
#     'start_date': datetime.now(),
#     'provide_context': True,
#     'depends_on_past': False,
#     'schedule_interval': None
# }
#
# dag = DAG('testcon', default_args=args)
#
#
# test_jdbc_con_task = JdbcOperator(task_id='select_data',
#                              dag=dag, jdbc_conn_id='jdbc_con',
#                              sql='select * from dwt_edw.cat_one_demo')