from datetime import datetime

IW_REST_DEFAULT_HOST = '54.174.145.91'
IW_REST_DEFAULT_PORT = 2999
IW_REST_DEFAULT_AUTH_TOKEN = 'aW5mb3dvcmtzOmFkbWluQGluZm93b3Jrcy5pbzoxMjM0NTY='

IW_REST_HOST = 'IW_REST_HOST'
IW_REST_AUTH_TOKEN = 'IW_REST_AUTH_TOKEN'
ROSIE_FLOW_DATASET_BASE_PATH = 'ROSIE_FLOW_DATASET_BASE_PATH'

POLLING_FREQUENCY_IN_SEC = 5
NUM_POLLING_RETRIES = 3

DAG_DEFAULT_CONFIG = {
    'owner': 'iw_admin',
    'start_date': datetime.now(),
    'provide_context': True,
    'depends_on_past': False
}
