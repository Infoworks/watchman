import sys
import os
from bson import ObjectId
import json
from utils import meteor, mongo, misc
import socket

g_test_object = {}
g_source_doc = {}
g_force_crawl = True


def main(config_path):
    global g_force_crawl

    g_force_crawl = True if os.getenv('crawl', 'true') == 'true' else False

    meteor.connect()
    create_source(config_path)
    misc.background_loop()


def create_source(config_path):
    global g_source_doc
    global g_test_object

    with open(config_path, 'r') as config_file:
        g_test_object = json.loads(config_file.read().replace('127.0.0.1', socket.getfqdn()))['config']

    if not g_test_object.get('name'):
        print 'Unable to get name of source!'
        misc.backround_process_terminate(False)
        return

    print 'Starting automation script for source: ' + g_test_object['name']

    template_filename = 'src_%s.json' % g_test_object['sourceType']
    with open('mongo_templates/' + template_filename, 'r') as config_file:
        source_template = config_file.read()
    replacements = {}
    for k, v in g_test_object.iteritems():
        replacements['##'+k.upper()+'##'] = v
    source_doc = json.loads(misc.replace_place_holders(source_template, replacements))

    if __debug__:
        print 'Configuration:'
        print json.dumps(source_doc, indent=4, sort_keys=True)

    mongo.job_name = source_doc['name']
    g_source_doc = mongo.client.sources.find_one({'name': source_doc['name']})
    if g_source_doc is None:
        print 'Inserting source.'
        meteor.client.call('insertSource', [source_doc], insert_source_callback)
    else:
        print 'Source already exists.'
        if g_force_crawl:
            # Update any change in the test configuration
            mongo.client.sources.update({'_id': g_source_doc['_id']}, {'$set': source_doc})
            g_source_doc = mongo.client.sources.find_one({'name': source_doc['name']})
            crawl_metadata_or_data()
        else:
            print 'Crawling skipped.'
            misc.backround_process_terminate(True)


def insert_source_callback(error, result):
    global g_source_doc

    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    print 'Done!'
    g_source_doc = mongo.client.sources.find_one({'_id': ObjectId(result)})
    crawl_metadata_or_data()


def crawl_metadata_or_data():
    global g_source_doc

    if g_source_doc['sourceType'] == 'rdbms':
        meteor.ddp_call(crawl_metadata)
    elif g_source_doc['sourceType'] == 'sftp':
        # Delete existing tables and add only the ones in the test configuration
        if g_source_doc.get('tables'):
            for table in g_source_doc['tables']:
                mongo.client.tables.delete_one({'_id': table})
            mongo.client.sources.update({'_id': g_source_doc['_id']}, {'$set': {'tables': []}})

        for table in g_test_object['tables']:
            table['source'] = g_source_doc['_id']
        table_ids = mongo.client.tables.insert_many(g_test_object['tables']).inserted_ids
        mongo.client.sources.update({'_id': g_source_doc['_id']}, {'$push': {'tables': {'$each': table_ids}}})
        g_source_doc = mongo.client.sources.find_one({'_id': g_source_doc['_id']})
        meteor.ddp_call(crawl_metadata)
    else:
        meteor.ddp_call(crawl_data)


def crawl_metadata():
    global g_source_doc

    connection = g_source_doc['connection']
    params = {
        'source': str(g_source_doc['_id']),
        'crawl': 'schema'
    }
    if g_source_doc['sourceType'] == 'rdbms':
        params['connection'] = connection
        params['overwrite'] = 'true'
    elif g_source_doc['sourceType'] == 'sftp':
        params['connection'] = connection
        params['hive_schema'] = g_source_doc['hive_schema']
        params['tables'] = [str(table_id) for table_id in g_source_doc['tables']]
    else:
        print 'Unknown source type ' + g_source_doc['sourceType']
        misc.backround_process_terminate()

    job = {
        'jobType': 'fetch_metadata',
        'queueingStatus': 'queued',
        'entityIdStr': str(g_source_doc['_id']),
        'entityType': 'source',
        'status': 'pending',
        'params': params,
    }

    print 'Queueing metadata crawling job.'
    if __debug__:
        print json.dumps(job)
    meteor.client.call('submitJobWithStringId', [job], crawl_metadata_callback)


def crawl_metadata_callback(error, result):
    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    job_id = result
    print 'Queued job with id: ' + job_id
    mongo.client.sources.update({'_id': g_source_doc['_id']}, {'$set': {'last_crawl_job': ObjectId(job_id)}})
    mongo.check_job_status(job_id, crawl_metadata_done_callback)


def crawl_metadata_done_callback(error, result):
    if error:
        misc.backround_process_terminate()
        return

    print 'Crawling metadata of source completed.'
    meteor.ddp_call(crawl_data)


def crawl_data():
    global g_source_doc

    connection = g_source_doc['connection']
    params = {'connection': connection}
    if g_source_doc['sourceType'] == 'sftp':
        params['crawl'] = 'data'
        params['source'] = str(g_source_doc['_id'])
        params['hive_schema'] = g_source_doc['hive_schema']
        params['tables'] = [{'_id': {'$type': 'oid', '$value': str(table_id)}} for table_id in g_source_doc['tables']]
    elif g_source_doc['sourceType'] == 'csv':
        params['tables'] = []
    elif g_source_doc['sourceType'] == 'rdbms':
        # Get the tables that need to be crawled and the partition keys for the tables
        tables = g_test_object.get('tables', [])
        table_list = []
        for t in tables:
            table_name = t['table']
            id = mongo.client.tables.find_one({'source': g_source_doc['_id'], 'table': table_name}, {'_id': True})
            mongo.client.tables.update(id, {'$set': t})
            t['_id'] = {'$type': 'oid', '$value': str(id['_id'])}
            table_list.append(t)
        tables = table_list

        params['overwrite'] = 'true'
        params['source'] = str(g_source_doc['_id'])
        params['crawl'] = 'data'
        params['tables'] = tables

    job = {
        'jobType': 'source_crawl',
        'queueingStatus': 'queued',
        'entityIdStr': str(g_source_doc['_id']),
        'entityType': 'source',
        'status': 'pending',
        'params': params,
    }

    print 'Queueing data crawling job.'
    if __debug__:
        print json.dumps(job)
    meteor.client.call('submitJobWithStringId', [job], crawl_data_callback)


def crawl_data_callback(error, result):
    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    job_id = result
    print 'Queued job with id: ' + job_id
    mongo.client.sources.update({'_id': g_source_doc['_id']}, {'$set': {'last_crawl_job': ObjectId(job_id)}})
    mongo.check_job_status(job_id, crawl_data_done_callback)


def crawl_data_done_callback(error, result):
    if error:
        misc.backround_process_terminate()
        return

    print 'Crawling data of source completed.'
    misc.backround_process_terminate(True)


if __name__ == '__main__':
    main(sys.argv[1])
    sys.exit(misc.g_exit_code)
