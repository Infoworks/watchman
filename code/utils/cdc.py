import json
from utils import meteor, mongo, misc
import socket
import time


def get_source_doc(config_path):
    with open(config_path, 'r') as config_file:
        test_object = json.loads(config_file.read().replace('127.0.0.1', socket.getfqdn()))['config']

    if not test_object.get('name'):
        print 'Unable to get name of source!'
        return

    source_doc = mongo.client.sources.find_one({'name': test_object.get('name')})
    if source_doc:
        return source_doc
    print 'Source: "%s" does not exist.' % test_object.get('name')


def get_cdc_tables(tables):
    ret = []
    for i in tables:
        table = mongo.client.tables.find_one({'_id': i}, {'configuration': True})
        if table['configuration'].get('sync_type', 'full-load') not in ('full-load', ''):
            ret.append({'_id': {'$type': 'oid', '$value': str(i)}})
    return ret


def do_job(job_type, entity_id, job_params):
    global job

    meteor.connect()
    job = {
        'entityIdStr': str(entity_id),
        'entityType': 'source',
        'jobType': job_type,
        'status': 'pending',
        'queueingStatus': 'queued',
        'params': job_params
    }
    if __debug__:
        print json.dumps(job)

    print 'Queueing the job.'
    time.sleep(5)  # Make sure client has connected before logging in
    meteor.ddp_call(job_submit)
    misc.background_loop()


def job_submit():
    meteor.client.call('submitJobWithStringId', [job], job_submit_callback)


def job_submit_callback(error, result):
    if error:
        print 'Error:', error
        misc.backround_process_terminate()
        return

    job_id = result
    print 'Queued job with id: ' + job_id
    mongo.check_job_status(job_id, job_done_callback)


def job_done_callback(error, _):
    if error:
        misc.backround_process_terminate()
        return
    misc.backround_process_terminate(True)
