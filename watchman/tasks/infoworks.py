import os
import sys
import inspect
import subprocess
import traceback

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import *
from job import *
from iw_utils import *
from utils.utils import load_json_config


def create_source(source_config_path, key_to_push_source_id=None, **kwargs):
    """
        Create a new source.

        :param source_config_path: path to JSON file with source configuration
        :param key_to_push_source_id: identifier where the newly created source id has to be inserted to be used in subsequent tasks
        :type source_config_path: string
        :type key_to_push_source_id: string

    """
    try:

        logging.info('Trying to create a new source.')
        
        path_to_json = get_config_value('ROSIE_FLOW_DATASET_BASE_PATH', kwargs) + source_config_path

        source_config = load_json_config(path_to_json)

        if source_config is None:
            logging.error('Unable to retrieve source configuration. Cannot create a new source.')
            sys.exit(1)

        logging.info('Source configuration is: ' + source_config)

        request = 'http://{ip}:{port}/v1.1/source/create.json?' \
                  'auth_token={auth_token}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs), port=IW_REST_DEFAULT_PORT,
                                                   auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs))

        response = process_response(requests.post(request, data=source_config))

        result = response.get('result', {})
        source_id = result.get('entity_id', None)

        logging.info('Source {id} has been created.'.format(id=source_id))

        if key_to_push_source_id is not None:
            kwargs['ti'].xcom_push(key=key_to_push_source_id, value=source_id)
        else:
            logging.warn('Unable to push source ID value into the key store')
            logging.warn('Subsequent task will not have access to the source ID from this task.')

    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error(traceback.print_exc())
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to create a new source.')
        sys.exit(1)


def crawl_metadata(source_config_path=None, task_id=None, key=None, **kwargs):
    """
        Submit a source metadata crawl job.

        :param source_config_path: path to JSON file where source name is specified
        :param task_id: identifier of a task instance using which the source id can be retrieved
        :param key: identifier that is dependent on task_id which can be used to retrieve source id
        :type source_config_path: string
        :type task_id: string
        :type key: string

    """
    try:
        source_id = None

        response = None

        if source_config_path:

            path_to_json = get_config_value('ROSIE_FLOW_DATASET_BASE_PATH', kwargs) + source_config_path
            
            source_config = load_json_config(path_to_json, False)
            if not source_config:
                logging.error('No source configuration specified. ')
                sys.exit(1)

            source_name = source_config.get('source_name', None)
            if not source_name:
                logging.error('Unable to retrieve source name from the config.')
                sys.exit(1)

            request = 'http://{ip}:{port}/v1.1/entity/id.json?entity_name={entity_name}&entity_type={entity_type}&' \
                      'auth_token={auth_token}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs), port=IW_REST_DEFAULT_PORT,
                                                       auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                                       entity_name=source_name, entity_type='source')

            response = process_response(requests.get(request))

            if response is None or response['result'] is None:
                logging.error('Unable to retrieve response for configuring tables and table groups from REST.')
                sys.exit(1)
            source_id = response['result']['entity_id']

        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id

        if source_id is None:
            logging.error('Unable to retrieve source ID. Cannot submit metadata crawl job.')
            sys.exit(1)

        request = 'http://{ip}:{port}/v1.1/source/crawl_metadata.json?source_id={source_id}&' \
                  'auth_token={auth_token}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs), port=IW_REST_DEFAULT_PORT,
                                                   auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                                   source_id=source_id)

        response = process_response(requests.post(request))

        if response is None or response['result'] is None:
            logging.error('Error while submitting job. Response is: ' + response)
            sys.exit(1)

        job_id = response['result']
        logging.info('Metadata crawl job has been submitted. Job ID is: {id}'.format(id=job_id))

        job_status, job_id = get_job_status(job_id, kwargs)
        if not job_status or job_status is False:
            logging.error('Job {j_id} failed to complete. '.format(j_id=job_id))
            sys.exit(1)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error(traceback.print_exc())
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to submit a source metadata crawl job')
        sys.exit(1)


def configure_tables_and_table_groups(table_group_config_path, source_id=None, task_id=None, key=None, **kwargs):
    """
        Configure tables and table groups for a source.

        :param table_group_config_path: path to JSON file where tables and table groups configuration is specified
        :param source_id: identifier for a source under which the table and table groups will be configured
        :param task_id: identifier of a task instance using which the source id can be retrieved
        :param key: identifier that is dependent on task_id which can be used to retrieve source id
        :type table_group_config_path: string
        :type source_id: string
        :type task_id: string
        :type key: string
    """
    try:
        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id

        if source_id is None:
            logging.error('Unable to retrieve source ID. Cannot create/configure tables or table groups.')
            sys.exit(1)

        path_to_json = get_config_value('ROSIE_FLOW_DATASET_BASE_PATH', kwargs) + table_group_config_path
        table_group_config = load_json_config(path_to_json)

        if table_group_config is None:
            logging.error('Unable to retrieve table group configuration. '
                          'Cannot create/configure tables or table groups.')
            sys.exit(1)

        request = 'http://{ip}:{port}/v1.1/source/table_groups/configure.json?source_id={source_id}&' \
                  'auth_token={auth_token}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs), port=IW_REST_DEFAULT_PORT,
                                                   auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                                   source_id=source_id)

        response = process_response(requests.post(request, data=table_group_config))

        if response is None or response['result'] is None:
            logging.error('Unable to retrieve response for configuring tables and table groups from REST.')
            sys.exit(1)
        return True
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error(traceback.print_exc())
        logging.error('Response from server: ', str(response))
        logging.error('Error occurred while trying to configure tables and table groups.')
        sys.exit(1)


def crawl_table_groups(task_id_for_table_group_id, table_group_key,
                       task_id_for_ingestion_type, ingestion_type_key, **kwargs):
    """
        Submit a crawl job for a table group present inside a source.

        :param task_id_for_table_group_id: identifier of a task instance using which the table group id can be retrieved
        :param table_group_key: identifier that is dependent on task_id which can be used to retrieve table group id
        :param task_id_for_ingestion_type: identifier of a task instance using which the ingestion type can be retrieved
        :param ingestion_type_key: identifier that is dependent on task_id which can be used to retrieve ingestion type
        :type task_id_for_table_group_id: string
        :type table_group_key: string
        :type task_id_for_ingestion_type: string
        :type ingestion_type_key: string

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
        logging.error(traceback.print_exc())
        logging.error('Error occurred while preparing to submit a source crawl job')
        sys.exit(1)


def crawl_table_groups_from_config(crawl_config_path, **kwargs):

    """
        Submit a crawl job for a table group defined in the JSON

        :param crawl_config_path: Path to JSON config specifying source name, table group name and ingestion type
        :type crawl_config_path: string

    """
    try:

        if crawl_config_path:

            path_to_json = get_config_value('ROSIE_FLOW_DATASET_BASE_PATH', kwargs) + crawl_config_path
            crawl_config = load_json_config(path_to_json, False)
            
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
                      '&parent_entity_type={parent_entity_type}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs),
                                                                        port=IW_REST_DEFAULT_PORT,
                                                                        auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                                                        entity_name=table_group_name,
                                                                        entity_type='table_group',
                                                                        parent_entity_name=source_name,
                                                                        parent_entity_type='source')
            response = process_response(requests.get(request))
            if response is None or response['result'] is None:
                logging.error('Error while trying to retrieve table group id. Response is: ' + str(response))
                sys.exit(1)

            table_group_id = response['result']['entity_id']
            _submit_ingestion_job(table_group_id, ingestion_type, kwargs)

    except Exception as e:
        logging.error('Exception: ', str(e))
        logging.error(traceback.print_exc())
        logging.error('Response from server is: ' + str(response))
        logging.error('Error occurred while preparing to submit a source crawl job')
        sys.exit(1)


def _submit_ingestion_job(table_group_id, ingestion_type, kwargs):
    try:
        request = 'http://{ip}:{port}/v1.1/source/table_group/ingest.json?auth_token={auth_token}&' \
                  'ingestion_type={ingestion_type}&table_group_id={table_group_id}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs),
                                                                                           port=IW_REST_DEFAULT_PORT,
                                                                                           auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                                                                           ingestion_type=ingestion_type,
                                                                                           table_group_id=table_group_id)

        response = process_response(requests.post(request))
        if response is None or response['result'] is None:
            logging.error('Error while submitting job. Response is: ' + str(response))
            sys.exit(1)
        # assuming a table group consists of only one type of tables (either all full load/incremental load)
        # TODO: launch multiple threads to track jobs

        job_id = response['result'][0]
        logging.info('Crawl job(s) have been submitted for '
                     'table group {t_id}. Job ID is: {id}'.format(id=str(job_id), t_id=str(table_group_id)))

        job_status, job_id = get_job_status(job_id, kwargs)
        if not job_status or job_status is False:
            logging.error('Job {j_id} failed to complete. '.format(j_id=job_id))
            sys.exit(1)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error(traceback.print_exc())
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to submit a source crawl job')
        sys.exit(1)


def source_setup(db_conf_path, script_path, **kwargs):
    try:
        db_conf_path = get_config_value('ROSIE_FLOW_DATASET_BASE_PATH', kwargs) + db_conf_path
        script_path = get_config_value('ROSIE_FLOW_DATASET_BASE_PATH', kwargs) + script_path
        if (not db_conf_path) or (not script_path):
            logging.error('DB configuration path or script path has not been specified. ')
            sys.exit(1)
        if not os.path.isfile(db_conf_path):
            logging.error('Path to DB config file is incorrect. '
                          'Please check the existence of {path}'.format(path=db_conf_path))
            sys.exit(1)
        if not os.path.isfile(script_path):
            logging.error('Path to script file is incorrect. '
                          'Please check the existence of {path}'.format(path=script_path))
            sys.exit(1)

        jar_command = 'java -cp {parent_dir}/resources/jars/* source.setup.SourceSetup ' \
                      '-dbConf {db_conf_path} -sqlScript ' \
                      '{sql_script_path}'.format(parent_dir=parent_dir,
                                                 db_conf_path=db_conf_path,
                                                 sql_script_path=script_path)

        logging.info('Jar command to be executed for DB setup: ' + jar_command)
        process = subprocess.Popen(jar_command, shell=True)
        process.communicate()

    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error(traceback.print_exc())
        logging.error('Error occurred while trying to setup source.')
        sys.exit(1)


def delete_source(delete_config_path=None, task_id=None, key=None, **kwargs):
    """
        Retrieves the source id from the json file passed as a param or from one the previous task instances.

        :param delete_config_path: path to json from where the source id can be retrieved
        :param task_id: identifier of the task from where the source id can be retrieved
        :param key: dictionary key to retrieve the source id
        :type delete_config_path: string
        :type task_id: string
        :type key: string
    """
    try:
        if delete_config_path:
            path_to_json = get_config_value('ROSIE_FLOW_DATASET_BASE_PATH', kwargs) + delete_config_path
            delete_config = load_json_config(path_to_json, False)
            if not delete_config:
                logging.error('No delete configuration specified. ')
                sys.exit(1)
            source_name = delete_config.get('source_name', None)

            if source_name is None:
                logging.error('Missing source_name from delete configuration.')
                sys.exit(1)

            request = 'http://{ip}:{port}/v1.1/entity/id.json?entity_name={entity_name}&entity_type={entity_type}&' \
                      'auth_token={auth_token}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs),
                                                       port=IW_REST_DEFAULT_PORT,
                                                       auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                                       entity_name=source_name, entity_type='source')
            response = process_response(requests.get(request))
            logging.info(response)
            if response is None or response['result'] is None:
                logging.error('Unable to retrieve source id from the source name. ')
                sys.exit(1)
            source_id = response['result']['entity_id']

        source_id = kwargs['ti'].xcom_pull(key=key, task_ids=task_id) if source_id is None else source_id

        _submit_delete_entity_job(source_id, 'source', kwargs)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error(traceback.print_exc())
        logging.error('Response from the server is: ' + str(response))
        logging.error('Error occurred while trying to delete a source.')
        sys.exit(1)


def _submit_delete_entity_job(entity_id, entity_type, kwargs):
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
                  'entity_type={entity_type}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs),
                                                     port=IW_REST_DEFAULT_PORT,
                                                     auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                                     entity_id=entity_id, entity_type=entity_type)
        response = process_response(requests.post(request))

        if response is None or response['result'] is None:
            logging.error('Error while submitting job. Response is: ' + str(response))
            sys.exit(1)

        job_id = response['result']
        logging.info('Delete entity job has been submitted for the entity. '
                     'Job ID is: {id}'.format(id=str(job_id)))

        job_status, job_id = get_job_status(job_id, kwargs)
        if not job_status or job_status is False:
            logging.error('Job {j_id} failed to complete. '.format(j_id=job_id))
            sys.exit(1)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error(traceback.print_exc())
        logging.error('Response from server: ' + str(response))
        logging.error('Error occurred while trying to submit a delete entity job')
        sys.exit(1)
