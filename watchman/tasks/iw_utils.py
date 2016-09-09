import ast
import os
import sys
import inspect
import logging

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import *

rest_host = None
rest_port = IW_REST_DEFAULT_PORT
rest_auth_token = None


def process_response(response):
    try:
        response = response.content
        response = response.replace('null', '"null"')
        response = ast.literal_eval(response)

        return response
    except Exception as e:
        return None


def get_dag_config(kwargs):
    try:
        return kwargs['dag_run'].conf
    except Exception as e:
        return {}


def get_config_value(key, kwargs):
    try:
        dag_config = get_dag_config(kwargs)
        return dag_config[key]
    except Exception as e:
        return None


def get_rest_ip(key, kwargs):
    global rest_host
    if rest_host is not None:
        return rest_host
    logging.info('Looking in DAG config for key: ' + key)
    config_value = get_config_value(key, kwargs)
    if config_value is None:
        logging.info('No key {key} found in DAG config'.format(key=key))
        logging.info('Using {key}'.format(key=IW_REST_DEFAULT_HOST))
        rest_host = IW_REST_DEFAULT_HOST
        return rest_host


def get_rest_auth_token(key, kwargs):
    global rest_auth_token
    if rest_auth_token is not None:
        return rest_auth_token
    config_value = get_config_value(key, kwargs)
    if config_value is None:
        logging.info('No key {key} found in DAG config'.format(key=key))
        logging.info('Using {key}'.format(key=IW_REST_DEFAULT_AUTH_TOKEN))
        rest_auth_token = IW_REST_DEFAULT_AUTH_TOKEN
        return rest_auth_token
