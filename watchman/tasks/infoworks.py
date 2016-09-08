import ast
import time
import requests
import logging
import os,sys,inspect
import subprocess

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import REST_HOST, REST_PORT, AUTH_TOKEN
from utils.utils import load_json_config


def create_source(source_config_path, key=None, **kwargs):
    """

    Create a new source.
    :param : source_config

    """
    try:

        logging.info('Trying to create a new source.')

        source_config = load_json_config(source_config_path)

        if source_config is None:
            logging.error('Unable to retrieve source configuration. Cannot create a new source.')
            sys.exit(1)

        logging.info('Source configuration is: ' + source_config)

        request = 'http://{ip}:{port}/v1.1/source/create.json?' \
                  'auth_token={auth_token}'.format(ip=REST_HOST, port=REST_PORT, auth_token=AUTH_TOKEN)

        response = _process_response(requests.post(request, data=source_config))

        result = response.get('result', {})
        source_id = result.get('entity_id', None)

        logging.info('Source {id} has been created.'.format(id=source_id))

        if key is not None:
            kwargs['ti'].xcom_push(key=key, value=source_id)
    
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to create a new source.')
        sys.exit(1)


def crawl_metadata(source_config_path=None, task_id=None, key=None, **kwargs):
    """
    Submit a source metadata crawl job.
    Params: source_name, task_id, key

    """
    try:
        response = None

        if source_config_path:

            source_config = load_json_config(source_config_path, False)
            if not source_config:
                logging.error('No source configuration specified. ')
                sys.exit(1)

            source_name = source_config.get('source_name', None)
            if not source_name:
                logging.error('Unable to retrieve source name from the config.')
                sys.exit(1)

            request = 'http://{ip}:{port}/v1.1/entity/id.json?entity_name={entity_name}&entity_type={entity_type}&' \
                      'auth_token={auth_token}'.format(ip=REST_HOST, port=REST_PORT, auth_token=AUTH_TOKEN,
                                                       entity_name=source_name, entity_type='source')

            response = _process_response(requests.get(request))

            if response is None or response['result'] is None:
                logging.error('Unable to retrieve response for configuring tables and table groups from REST.')
                sys.exit(1)
            source_id = response['result']['entity_id']

        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id

        if source_id is None:
            logging.error('Unable to retrieve source ID. Cannot submit metadata crawl job.')
            sys.exit(1)

        request = 'http://{ip}:{port}/v1.1/source/crawl_metadata.json?source_id={source_id}&' \
                  'auth_token={auth_token}'.format(ip=REST_HOST, port=REST_PORT, auth_token=AUTH_TOKEN,
                                                   source_id=source_id)

        response = _process_response(requests.post(request))

        if response is None or response['result'] is None:
            logging.error('Error while submitting job. Response is: ' + response)
            sys.exit(1)

        job_id = response['result']
        logging.info('Metadata crawl job has been submitted. Job ID is: {id}'.format(id=job_id))

        status = get_job_status(job_id)
        if not status:
            sys.exit(1)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to submit a source metadata crawl job')
        sys.exit(1)


def configure_tables_and_table_groups(table_group_config_path, source_id=None, task_id=None, key=None, **kwargs):
    """
    Configure tables and table groups for a source.
    Params: table_group_config, source_id, task_id

    """
    try:
        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id

        if source_id is None:
            logging.error('Unable to retrieve source ID. Cannot create/configure tables or table groups.')
            sys.exit(1)
        table_group_config = load_json_config(table_group_config_path)

        if table_group_config is None:
            logging.error('Unable to retrieve table group configuration. '
                          'Cannot create/configure tables or table groups.')
            sys.exit(1)

        request = 'http://{ip}:{port}/v1.1/source/table_groups/configure.json?source_id={source_id}&' \
                  'auth_token={auth_token}'.format(ip=REST_HOST, port=REST_PORT, auth_token=AUTH_TOKEN,
                                                   source_id=source_id)

        response = _process_response(requests.post(request, data=table_group_config))

        if response is None or response['result'] is None:
            logging.error('Unable to retrieve response for configuring tables and table groups from REST.')
            sys.exit(1)
        return True
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Response from server: ', str(response))
        logging.error('Error occurred while trying to configure tables and table groups.')
        sys.exit(1)


def crawl_table_groups(task_id_for_table_group_id, table_group_key,
                       task_id_for_ingestion_type, ingestion_type_key, **kwargs):
    """
    Submit a crawl job for all table groups present inside a source.
    Params: source_id, task_id

    """

    try:
        table_group_id = kwargs['ti'].xcom_pull(key=table_group_key, task_ids=task_id_for_table_group_id)

        if table_group_id is None:
            logging.error('Unable to retrieve source ID. Cannot crawl table group.')
            sys.exit(1)

        ingestion_type = kwargs['ti'].xcom_pull(key=ingestion_type_key, task_ids=task_id_for_ingestion_type)
        if ingestion_type is None:
            logging.error('Unable to retrieve ingestion type. Cannot crawl table group.')
            sys.exit(1)

        _submit_ingestion_job(table_group_id, ingestion_type)

    except Exception as e:
        logging.error('Exception: ', str(e))
        logging.error('Error occurred while preparing to submit a source crawl job')
        sys.exit(1)


def crawl_table_groups_from_config(crawl_config_path):

    """
    Submit a crawl job for all table groups present inside a source.
    Params: Path to JSON config

    """
    try:

        if crawl_config_path:
            crawl_config = load_json_config(crawl_config_path, False)
            if not crawl_config:
                logging.error('No crawl configuration specified. ')
                sys.exit(1)

            source_name = crawl_config.get('source_name', None)
            table_group_name = crawl_config.get('table_group_name', None)
            ingestion_type = crawl_config.get('ingestion_type', None)

            if not source_name or not table_group_name or not ingestion_type:
                logging.error('Missing input in crawl configuration.')
                sys.exit(1)

            request = 'http://{ip}:{port}/v1.1/entity/id.json?auth_token={auth_token}&entity_type={entity_type}' \
                      '&entity_name={entity_name}&parent_entity_name={parent_entity_name}' \
                      '&parent_entity_type={parent_entity_type}'.format(ip=REST_HOST, port=REST_PORT,
                                                                        auth_token=AUTH_TOKEN,
                                                                        entity_name=table_group_name,
                                                                        entity_type='table_group',
                                                                        parent_entity_name=source_name,
                                                                        parent_entity_type='source')
            response = _process_response(requests.get(request))
            if response is None or response['result'] is None:
                logging.error('Error while trying to retrieve table group id. Response is: ' + str(response))
                sys.exit(1)

            table_group_id = response['result']['entity_id']
            _submit_ingestion_job(table_group_id, ingestion_type)

    except Exception as e:
        logging.error('Exception: ', str(e))
        logging.error('Error occurred while preparing to submit a source crawl job')
        sys.exit(1)


def _submit_ingestion_job(table_group_id, ingestion_type):
    try:
        request = 'http://{ip}:{port}/v1.1/source/table_group/ingest.json?auth_token={auth_token}&' \
                  'ingestion_type={ingestion_type}&table_group_id={table_group_id}'.format(ip=REST_HOST,
                                                                                           port=REST_PORT,
                                                                                           auth_token=AUTH_TOKEN,
                                                                                           ingestion_type=ingestion_type,
                                                                                           table_group_id=table_group_id)

        response = _process_response(requests.post(request))
        if response is None or response['result'] is None:
            logging.error('Error while submitting job. Response is: ' + str(response))
            sys.exit(1)
        # assuming a table group consists of only one type of tables (either all full load/incremental load)
        # TODO: launch multiple threads to track jobs

        job_id = response['result'][0]
        logging.info('Crawl job(s) have been submitted for '
                     'table group {t_id}. Job ID is: {id}'.format(id=str(job_id), t_id=str(table_group_id)))

        job_status = get_job_status(job_id)
        if not job_status:
            logging.error('Job {j_id} failed to complete. '.format(j_id=job_id))
            sys.exit(1)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to submit a source crawl job')
        sys.exit(1)


def source_setup(db_conf_path, script_path, task_id=None, key=None, **kwargs):
    try:
        if db_conf_path and script_path:
            jar_command = 'java -cp ../utils/AutomationUtils.jar:../utils/jars/*:. source.setup.SourceSetup -dbConf ' \
                          + db_conf_path + ' -sqlScript ' + script_path
            process = subprocess.Popen(jar_command)
            process.communicate()
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Error occurred while trying to setup source.')
        sys.exit(1)


def delete_source(delete_config_path=None, task_id=None, key=None, **kwargs):
    """
        Retrieves the source id from the json file passed as a param or from one the previous task instances.
        :param: delete_config_path: path to json from where the source id can be retrieved
        :type: delete_config_path: string
        :param: task_id: identifier of the task from where the source id can be retrieved
        :type: task_id: string
        :param: key: dictionary key to retrieve the source id
        :type: key: string
    """
    try:
        if delete_config_path:

            delete_config = load_json_config(delete_config_path, False)
            if not delete_config:
                logging.error('No delete configuration specified. ')
                sys.exit(1)
            source_name = delete_config.get('source_name', None)

            if source_name is None:
                logging.error('Missing source_name from delete configuration.')
                sys.exit(1)

            request = 'http://{ip}:{port}/v1.1/entity/id.json?entity_name={entity_name}&entity_type={entity_type}&' \
                      'auth_token={auth_token}'.format(ip=REST_HOST, port=REST_PORT, auth_token=AUTH_TOKEN,
                                                       entity_name=source_name, entity_type='source')
            response = _process_response(requests.get(request))

            if response is None or response['result'] is None:
                logging.error('Unable to retrieve source id from the source name. ')
                sys.exit(1)
            source_id = response['result']['entity_id']

        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id

        _submit_delete_entity_job(source_id, 'source')
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Error occurred while trying to delete a source.')
        sys.exit(1)


def _submit_delete_entity_job(entity_id, entity_type):
    """
        Submit a delete job
        :param: entity_id: identifier for the entity
        :type: entity_id: string
        :param: entity_type: type of the entity
        :type: entity_type: string
    """
    try:

        request = 'http://{ip}:{port}/v1.1/entity/delete.json?' \
                  'auth_token={auth_token}&entity_id={entity_id}&' \
                  'entity_type={entity_type}'.format(ip=REST_HOST, port=REST_PORT, auth_token=AUTH_TOKEN,
                                                     entity_id=entity_id, entity_type=entity_type)
        response = _process_response(requests.post(request))

        if response is None or response['result'] is None:
            logging.error('Error while submitting job. Response is: ' + str(response))
            sys.exit(1)

        job_id = response['result']
        logging.info('Delete entity job has been submitted for the entity. '
                     'Job ID is: {id}'.format(id=str(job_id)))

        job_status = get_job_status(job_id)
        if not job_status:
            logging.error('Job {j_id} failed to complete. '.format(j_id=job_id))
            sys.exit(1)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to submit a delete entity job')
        sys.exit(1)


def get_job_status(job_id):
    """
        Get IW job status
        :param: job_id: job id to poll the status
        :type: job_id: string
        :returns: job status
        :rtype: bool
    """
    while True:
        try:

            request = 'http://{ip}:{port}/v1.1/job/status.json?auth_token={auth_token}&' \
                      'job_id={job_id}'.format(ip=REST_HOST, port=REST_PORT,
                                               auth_token=AUTH_TOKEN, job_id=str(job_id))

            response = _process_response(requests.get(request))

            if response is None or response['result'] is None:
                logging.error('Unable to retrieve job status.')
                sys.exit(1)

            job_status = response['result'].get('status')

            if job_status == 'completed':
                return True, job_id

            if job_status in ['pending']:
                logging.info('Job status currently is: {job_status}'.format(job_status=job_status))
                continue

            if job_status in ['running']:
                logging.info('Job status: ', str(response['result']))
                continue

            if job_status in ['blocked', 'failed', 'canceled']:
                return False, job_id

            time.sleep(7)
        except Exception as e:
            logging.error('Exception: ' + str(e))
            logging.error('Error occurred while trying to poll job status.')
            sys.exit(1)


def _process_response(response):
    try:
        response = response.content
        response = response.replace('null', '"null"')
        response = ast.literal_eval(response)

        return response
    except Exception as e:
        return None
