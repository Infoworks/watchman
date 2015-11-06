import sys
import datetime
import time
import json
import socket
import requests
from utils import mongo
from config.config import config


def main(config_path):
    with open(config_path, 'r') as config_file:
        entity_info = json.loads(config_file.read().replace('127.0.0.1', socket.getfqdn()))
    test_object = entity_info['config']
    entity_type = test_object['entityType']
    entity_name = test_object['name']

    if not (entity_name or entity_type):
        print 'Unable to get entity information!'
        return -1

    entity_doc = None
    if entity_type == 'datamodel':
        entity_doc = mongo.client.datamodels.find_one({'name': entity_name})
    elif entity_type == 'cube':
        entity_doc = mongo.client.cubes.find_one({'name': entity_name})
    if entity_doc is None:
        print '{entity_type}: {entity_name} does not exist.'.format(entity_type=entity_type, entity_name=entity_name)
        return -1

    entity_id = str(entity_doc['_id'])
    params = {}
    if entity_type == 'datamodel':
        params['datamodelId'] = entity_id
        job_type = 'datamodel_build'
    else:  # entity_type == 'cube':
        params['cubeId'] = entity_id
        job_type = 'cube_build'
    params['path'] = '/opt/infoworks'

    job = {
        'jobType': job_type,
        'queueingStatus': 'queued',
        'entityId': entity_id,
        'entityType': entity_type,
        'status': 'pending',
        'params': params,
    }
    if __debug__:
        print json.dumps(job)

    start_time = datetime.datetime.now() + datetime.timedelta(minutes=3)
    url = 'http://{ip}:{port}/ActivityScheduler/schedule/submit/?' \
          'starts_on={starts_on}&time_hour={time_hour}&time_min={time_min}&repeat_interval=never&' \
          'repeat_on=&ends_after=0&entityId={entity_id}&entityType={entity_type}&jobType={job_type}'. \
        format(
            ip=config.get('scheduler_host'),
            port=config.get('scheduler_port'),
            starts_on=time.strftime("%m/%d/%Y"),
            time_hour='%02d' % start_time.hour,
            time_min='%02d' % start_time.minute,
            entity_id=entity_id,
            entity_type=entity_type,
            job_type=job_type
        )

    try:
        requests.post(url, json.dumps(job))
    except (requests.ConnectionError, requests.HTTPError) as e:
        print 'Could not connect to REST service/Invalid response code.'
        print e.message
        return -1

    print 'Build job submitted successfully.'
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
