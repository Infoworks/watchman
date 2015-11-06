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
        test_object = json.loads(config_file.read().replace('127.0.0.1', socket.getfqdn()))['config']

    if not test_object.get('name'):
        print 'Unable to get the name of source!'
        return -1

    source_doc = mongo.client.sources.find_one({'name': test_object.get('name')})
    if source_doc is None:
        print 'Source: "%s" does not exist.' % test_object.get('name')
        return -1

    entity_id = str(source_doc['_id'])
    start_time = datetime.datetime.now() + datetime.timedelta(minutes=3)
    url = 'http://{ip}:{port}/ActivityScheduler/schedule/submit/?' \
          'starts_on={starts_on}&time_hour={time_hour}&time_min={time_min}&repeat_interval=never&' \
          'repeat_on=&ends_after=0&entityId={entity_id}&entityType=source&jobType=source_crawl'. \
        format(
            ip=config.get('scheduler_host'),
            port=config.get('scheduler_port'),
            starts_on=time.strftime("%m/%d/%Y"),
            time_hour='%02d' % start_time.hour,
            time_min='%02d' % start_time.minute,
            entity_id=entity_id
        )

    params = {}
    if test_object['sourceType'] == 'csv':
        params['fileType'] = test_object['fileType']
        params['inputDir'] = test_object['path']
        params['seperator'] = test_object['separator']
        params['quotechar'] = test_object['quotechar']
        params['escapechar'] = test_object['escapechar']
        params['schema'] = test_object['schema']
    elif test_object['sourceType'] == 'json':
        params['fileType'] = test_object['fileType']
        params['inputDir'] = test_object['path']
    elif test_object['sourceType'] == 'rdbms':
        params['database'] = test_object['database']
        params['driver'] = test_object['driver_name']
        params['dns'] = test_object['dns']
        params['private_key'] = test_object['private_key']
        params['schema'] = test_object['schema']
        params['overwrite'] = 'true'
        params['source'] = entity_id
        params['url'] = test_object['connection_string']
        params['username'] = test_object['username']
        params['password'] = test_object['password']
        params['crawl'] = 'data'

    job = {
        'jobType': 'source_crawl',
        'queueingStatus': 'queued',
        'entityId': str(entity_id),
        'entityType': 'source',
        'status': 'pending',
        'params': params,
    }
    if __debug__:
        print json.dumps(job)

    try:
        requests.post(url, json.dumps(job))
    except (requests.ConnectionError, requests.HTTPError) as e:
        print 'Could not connect to REST service/Invalid response code.'
        print e.message
        return -1

    print 'Crawl job submitted successfully.'
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
