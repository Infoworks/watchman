import ast
import time
import requests
import os,sys,inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import REST_HOST, REST_PORT, IW_USERNAME, IW_PASSWORD
from utils.utils import load_json_config


def create_source(source_config_path, task_id=None, key=None, **kwargs):
    """

    Create a new source.
    Params: source_config, task_id

    """
    try:
        print 'Trying to create a new source.'
        source_config = load_json_config(source_config_path)
        if source_config is None:
            print 'Unable to retrieve source configuration. Cannot create a new source.'
            sys.exit(1)
        print 'Source configuration is: ', source_config
        request = 'http://{ip}:{port}/v1.1/source/create.json?' \
                  'user={user_name}&pass={password}'.format(ip=REST_HOST, port=REST_PORT,
                                                            user_name=IW_USERNAME, password=IW_PASSWORD)
        response = None
        response = requests.post(request, data=source_config)
        response = response.content
        response = response.replace('null', '"null"')
        response = ast.literal_eval(response)
        result = response.get('result', {})
        source_id = result.get('entity_id', None)
        print 'Source {id} has been created.'.format(id=source_id)
        kwargs['ti'].xcom_push(key=key, value=source_id)
    except Exception as e:
        print 'Exception: ', e
        print 'Response from server: ', response
        print 'Error occurred while trying to create a new source.'
        sys.exit(1)


def crawl_metadata(source_id=None, task_id=None, key=None, **kwargs):
    """
    Submit a source metadata crawl job.
    Params: source_id, task_id

    """
    try:
        response = None
        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id
        if source_id is None:
            print 'Unable to retrieve source ID. Cannot submit metadata crawl job.'
            sys.exit(1)
        request = 'http://{ip}:{port}/v1.1/source/crawl_metadata.json?source_id={source_id}&' \
                  'user={user_name}&pass={password}'.format(ip=REST_HOST, port=REST_PORT, user_name=IW_USERNAME,
                                                            password=IW_PASSWORD, source_id=source_id)

        response = requests.post(request)
        response = response.content
        response = response.replace('null', '"null"')
        response = ast.literal_eval(response)
        if response is None or response['result'] is None:
            print 'Error while submitting job. Response is: ', response
            sys.exit(1)
        job_id = response['result']
        print 'Metadata crawl job has been submitted. Job ID is: {id}'.format(id=job_id)
        status = get_job_status(job_id)
        if not status:
            sys.exit(1)
    except Exception as e:
        print 'Exception: ', e
        print 'Response from server: ', response
        print 'Error occurred while trying to submit a source metadata crawl job'
        sys.exit(1)


def configure_tables_and_table_groups(table_group_config_path, source_id=None, task_id=None, key=None, **kwargs):
    """
    Configure tables and table groups for a source.
    Params: table_group_config, source_id, task_id

    """
    try:
        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id
        if source_id is None:
            print 'Unable to retrieve source ID. Cannot create/configure tables or table groups.'
            sys.exit(1)
        table_group_config = load_json_config(table_group_config_path)
        if table_group_config is None:
            print 'Unable to retrieve table group configuration. Cannot create/configure tables or table groups.'
            sys.exit(1)
        request = 'http://{ip}:{port}/v1.1/source/table_groups/configure.json?source_id={source_id}&user={user_name}&' \
                  'pass={password}'.format(ip=REST_HOST, port=REST_PORT, user_name=IW_USERNAME,
                                           password=IW_PASSWORD, source_id=source_id)
        response = None
        response = requests.post(request, data=table_group_config)
        response = response.content
        response = response.replace('null', '"null"')
        response = ast.literal_eval(response)
        if response is None or response['result'] is None:
            print 'Unable to retrieve response for configuring tables and table groups from REST.'
            sys.exit(1)
        return True
    except Exception as e:
        print 'Exception: ', e
        print 'Response from server: ', response
        print 'Error occurred while trying to configure tables and table groups.'
        sys.exit(1)


def crawl_table_groups(source_id=None, task_id=None, key=None, **kwargs):
    """
    Submit a crawl job for all table groups present inside a source.
    Params: source_id, task_id

    """

    try:
        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id
        if source_id is None:
            print 'Unable to retrieve source ID. Cannot crawl table group.'
            sys.exit(1)
        request = 'http://{ip}:{port}/v1.1/source/table_groups.json?' \
                  'user={user_name}&pass={password}&' \
                  'source_id={source_id}'.format(
                                                ip=REST_HOST, port=REST_PORT, user_name=IW_USERNAME,
                                                password=IW_PASSWORD, source_id=source_id)
        response = requests.get(request)
        response = response.content
        response = response.replace('null', '"null"')
        response = ast.literal_eval(response)
        if response is None or response['result'] is None:
            print 'Unable to retrieve table group list from the source.'
            sys.exit(1)
        for table_group in response['result']:
            table_group_id = table_group['id']
            request = 'http://{ip}:{port}/v1.1/source/table_group/ingest.json?' \
                      'user={user_name}&pass={password}&ingestion_type={ingestion_type}&' \
                      'table_group_id={table_group_id}'.format(
                                                    ip=REST_HOST, port=REST_PORT, user_name=IW_USERNAME,
                                                    password=IW_PASSWORD,
                                                    ingestion_type='source_all', table_group_id=table_group_id)

            response = requests.post(request)
            response = response.content
            response = response.replace('null', '"null"')
            response = ast.literal_eval(response)
            if response is None or response['result'] is None:
                print 'Error while submitting job. Response is: ', response
                sys.exit(1)
            job_id = response['result'][0]
            print 'Crawl job(s) have been submitted for table group ' \
                  '{t_id}. Job ID is: {id}'.format(id=str(job_id), t_id=table_group_id)
            job_status = get_job_status(job_id)
            if not job_status:
                print 'Job {j_id} failed to complete. '.format(j_id=job_id)
                sys.exit(1)
    except Exception as e:
        print 'Exception: ', e
        print 'Response from server: ', response
        print 'Error occurred while trying to submit a source crawl job'
        sys.exit(1)


def get_job_status(job_id):
    """
    Get infoworks job status
    Params: job_id

    """
    while True:
        try:
            request = 'http://{ip}:{port}/v1.1/job/status.json?user={user_name}&pass={password}&' \
                      'job_id={job_id}'.format(ip=REST_HOST, port=REST_PORT,
                                               user_name=IW_USERNAME,
                password=IW_PASSWORD, job_id=str(job_id))
            response = requests.get(request)
            response = response.content
            response = response.replace('null', '"null"')
            response = ast.literal_eval(response)
            if response is None or response['result'] is None:
                print 'Unable to retrieve job status.'
                sys.exit(1)
            job_status = response['result'].get('status')
            if job_status == 'completed':
                return True, job_id
            if job_status in ['pending']:
                print 'Job status currently is: {job_status}'.format(job_status=job_status)
                continue
            if job_status in ['running']:
                print 'Job status: ', str(response['result'])
                continue
            if job_status in ['blocked', 'failed', 'canceled']:
                return False, job_id
            time.sleep(7)
        except Exception as e:
            print 'Exception: ', e
            print 'Error occurred while trying to poll job status.'
            sys.exit(1)
