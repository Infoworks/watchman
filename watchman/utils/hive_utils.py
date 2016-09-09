from builtins import range
from airflow.operators import HiveOperator
from airflow.models import DAG
from datetime import datetime, timedelta
from airflow.hooks.hive_hooks import HiveServer2Hook
import time

"""
HiveUtil to execute a query on Hive Database
:param hive_conn_id: name of the connection. It should have been configured in airflow beforehand. (admin-> connections)
:type flow_name: string
:qry: the query to be executed
:type dataset_name: string
:returns: result Execution status of the flow
:rtype: boolean
"""


def execute_hive_query(hive_conn_id, qry):
    # hook = HiveServer2Hook(hiveserver2_conn_id="hiveserver2_ndev3")
    hook = HiveServer2Hook(hive_conn_id)
    recs = hook.get_records(qry)
    print(recs)
    return recs


print(execute_hive_query("hiveserver2_ndev3", "select count(1) from oracle_northwind_full_load.orders"))
