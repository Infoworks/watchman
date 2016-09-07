from datetime import datetime
from airflow import DAG
from airflow.operators.jdbc_operator import JdbcOperator
import os, sys, inspect

args = {
    'owner': 'iw_admin',
    'start_date': datetime.now(),
    'provide_context': True,
    'depends_on_past': False,
    'schedule_interval': None
}

dag = DAG('testJDBC6', default_args=args)


test_jdbc_task = JdbcOperator(task_id='select_stuff',dag=dag,
            jdbc_url='jdbc:teradata://ec2-54-144-76-210.compute-1.amazonaws.com/TMODE=ANSI,database=dwt_edw,USER=dbc,PASSWORD=infoworks',
            jdbc_driver_name='com.teradata.jdbc.TeraDriver',
            jdbc_driver_loc='/Users/thejas/dblore/artifacts/lib/teradata/terajdbc4.jar',
            sql='select * from dwt_edw.cat_one_demo')
