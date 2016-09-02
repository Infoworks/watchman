from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os,sys,inspect,argparse,json
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

parser = argparse.ArgumentParser()
parser.add_argument('--database', help='Database Type Teradata or Oracle etc..')
parser.add_argument('--sourceName', help='name for the new source to be created')
parser.add_argument('--sourceConfig', help='source config json file path')
parser.add_argument('--tableGroupConfig', help='table group config json file path')
scriptArgs = parser.parse_args()

def readJsonFile(filePath):
    jsonFile = open(filePath, "r")
    data = json.load(jsonFile)
    jsonFile.close()
    return data

def readJsonFileAsString(filePath):
    return json.dumps(readJsonFile(filePath))

def newSourceConfig(data,sourceName):
    data["configuration"]["name"] = sourceName
    data["configuration"]["hdfs_path"] = "/iw/sources/" + sourceName
    data["configuration"]["hive_schema"] = sourceName
    return json.dumps(data)

dag = DAG('workflow_18', default_args=args)

source_name = scriptArgs.sourceName
source_config = newSourceConfig(readJsonFile(scriptArgs.sourceConfig),source_name)
table_group_config = readJsonFileAsString(scriptArgs.tableGroupConfig)
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
