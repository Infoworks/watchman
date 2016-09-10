import logging
import time
import sys
import os
import inspect
import requests

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config.configuration import *
from iw_utils import *


def get_job_status(job_id, kwargs):
    """

        Get IW job status
        :param: job_id: job id to poll the status
        :type: job_id: string
        :returns: job status
        :rtype: bool

    """

    logging.info('Polling frequency has been set to: {sec}'.format(sec=POLLING_FREQUENCY_IN_SEC))

    num_poll_retries = 0

    while True:
        try:

            request = 'http://{ip}:{port}/v1.1/job/status.json?auth_token={auth_token}&' \
                      'job_id={job_id}'.format(ip=get_rest_ip(IW_REST_HOST, kwargs),
                                               port=IW_REST_DEFAULT_PORT,
                                               auth_token=get_rest_auth_token(IW_REST_AUTH_TOKEN, kwargs),
                                               job_id=str(job_id))

            response = process_response(requests.get(request))

            if response is None or response['result'] is None:
                logging.error('Unable to retrieve job status.')
                sys.exit(1)

            job_status = response['result'].get('status')

            if job_status == 'completed':
                logging.info('Job finished successfully.')
                return True, job_id

            if job_status in ['pending']:
                logging.info('Job status currently is: {job_status}'.format(job_status=job_status))
                time.sleep(POLLING_FREQUENCY_IN_SEC)
                continue

            if job_status in ['running']:
                logging.info('Job status: running, Percent complete: ' +
                             str(round(response['result']['percentCompleted'], 1)) + '%')
                time.sleep(POLLING_FREQUENCY_IN_SEC)
                continue

            if job_status in ['blocked']:
                logging.warn('Job is currently blocked.')
                return False, job_id

            if job_status in ['failed']:
                logging.error('Job failed to execute.')
                return False, job_id

            if job_status in ['canceled']:
                logging.warn('Job has been manually cancelled.')
                return False, job_id

        except Exception as e:
            logging.error('Exception: ' + str(e))
            logging.error('Error occurred while trying to poll job status.')
            if num_poll_retries < NUM_POLLING_RETRIES:
                num_poll_retries += 1
                logging.info('Retry after: {poll_freq_in_sec} second(s).'
                             .format(poll_freq_in_sec=POLLING_FREQUENCY_IN_SEC))
                time.sleep(POLLING_FREQUENCY_IN_SEC)
                logging.info('Retry attempt: ' + str(num_poll_retries))
                continue
            logging.info('Maximum retries exceeded. Exiting.')
            sys.exit(1)
