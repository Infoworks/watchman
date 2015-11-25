import sys
import os
from bson import ObjectId
import json
from utils import meteor, mongo, misc

g_dm_object = {}
g_datamodel_doc = {}
g_cube_object = {}
g_config_path = ''
g_force_build = True


def main(config_path):
    global g_config_path, g_force_build
    g_config_path = config_path
    g_force_build = True if os.getenv('build_datamodel', 'true') == 'true' else False

    meteor.connect()
    check_config()
    misc.background_loop()

    # datamodel build and validation is completed, build cubes if any now
    if misc.g_exit_code != 0:
        return

    check_cube()


def check_config():
    global g_config_path
    global g_dm_object

    g_dm_object = {}
    with open(g_config_path, 'r') as config_file:
        g_dm_object = json.loads(config_file.read())['config']

    if not g_dm_object.get('name'):
        print 'Unable to get name of datamodel!'
        misc.backround_process_terminate()
        return

    print 'Starting automation script for datamodel: ' + g_dm_object['name']

    mongo.job_name = g_dm_object['name']
    if __debug__:
        print 'Configuration:'
        print json.dumps(g_dm_object, indent=4, sort_keys=True)

    # check sources
    if g_dm_object.get('sources') is None:
        print 'Sources not specified!'
        misc.backround_process_terminate()
        return
    check_for_sources(g_dm_object)

    # check domain
    if g_dm_object.get('domain') is None:
        print 'Domain not specified!'
        misc.backround_process_terminate()
        return
    check_for_domain(g_dm_object)


def check_for_sources(dm_object):
    print 'Checking sources:'
    for s in dm_object['sources']:
        source_doc = mongo.client.sources.find_one({'name': s})
        if source_doc is None:
            print "Source '%s' doesn't exist. Please crawl it before building this datamodel." % s
            misc.backround_process_terminate(False)
            return
        else:
            print "Source '%s' exists." % s
    print 'All sources exist.'


def check_for_domain(dm_object):
    print "Checking if domain '%s' exists" % dm_object['domain']

    domain_doc = mongo.client.domains.find_one({'name': dm_object['domain']})
    if domain_doc:
        print 'Domain exists.'
        check_and_add_domain_sources()
    else:
        print "Domain doesn't exist. Creating it."
        meteor.ddp_call(create_domain)


def create_domain():
    global g_dm_object

    new_domain = {
        'name': g_dm_object['domain'],
        'description': 'Test Domain',
    }
    meteor.client.call('insertDomain', [new_domain], insert_domain_callback)


def insert_domain_callback(error, result):
    if error:
        misc.backround_process_terminate()
        return
    
    print 'Done!'
    check_and_add_domain_sources()


def check_and_add_domain_sources():
    print 'Checking if the sources are added to the domain.'

    source_ids = []
    source_docs = mongo.client.sources.find({'name': {'$in': g_dm_object['sources']}})
    for s in source_docs:
        source_ids.append(s['_id'])

    domain_doc = mongo.client.domains.find_one({'name': g_dm_object['domain']})
    domain_id = domain_doc['_id']
    domain_sources_doc = mongo.client.domain_sources.find_one({'domain': domain_id})

    if domain_sources_doc is None:  # no document
        print 'Creating domain_sources document.'
        domain_sources_doc = {
            'domain': domain_id,
            'sources': source_ids,
        }
        if __debug__:
            print domain_sources_doc

        mongo.client.domain_sources.insert(domain_sources_doc)
    else:
        print 'Updating domain_sources document.'
        domain_sources = domain_sources_doc['sources']
        updated_domain_sources = domain_sources + list(set(source_ids) - set(domain_sources))
        mongo.client.domain_sources.update({'domain': ObjectId(domain_id)}, 
                                           {'$set': {'sources': updated_domain_sources}})
    create_datamodel(g_dm_object, domain_id)


def create_datamodel(dm_object, domain_id):
    global g_datamodel_doc
    g_datamodel_doc = mongo.client.datamodels.find_one({'name': dm_object['name']})

    if g_datamodel_doc is None:
        print 'Creating datamodel.'
        meteor.client.call('insertDatamodel', [dm_object['name'], 'Test Datamodel', str(domain_id)],
                           insert_datamodel_callback)
    else:
        print 'Datamodel already exists.'
        if g_force_build:
            design_datamodel()  # Update any change in the test configuration
        else:
            print 'Building datamodel skipped.'
            misc.backround_process_terminate(True)


def insert_datamodel_callback(error, result):
    global g_datamodel_doc

    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return
    
    print 'Done!'
    if __debug__:
        print result
    g_datamodel_doc = mongo.client.datamodels.find_one({'_id': ObjectId(result)})
    design_datamodel()


def design_datamodel():
    global g_dm_object

    print 'Designing datamodel.'
    treemap = g_dm_object['treemap']
    if not replace_table_with_dm_table(treemap):
        return
    mongo.client.datamodels.update({'name': g_dm_object['name']}, {'$set': {
        'treemap': treemap,
        'hive_schema': g_dm_object['name'],
        'hdfs_path': '/datamodels/iw/' + g_dm_object['name']}
    })

    meteor.ddp_call(build_datamodel)


def replace_table_with_dm_table(node):
    table_id = get_datamodel_table_id_for_table(node['source'], node['table'])
    if not table_id:
        return

    node['datamodelTableId'] = table_id
    del node['table']
    del node['source']

    if node.get('children'):
        for n in node['children']:
            if not replace_table_with_dm_table(n):
                return
    return node


def get_datamodel_table_id_for_table(source, table):
    source_doc = mongo.client.sources.find_one({'name': source})
    if source_doc is None:
        print 'Unable to find source "%s"!' % source
        misc.backround_process_terminate(False)
        return

    table_doc = mongo.client.tables.find_one({'source': source_doc['_id'], 'table': table})
    if table_doc is None:
        print 'Unable to find table "%s" in source "%s"!' % (table, source)
        misc.backround_process_terminate(False)
        return

    dm_table_doc = mongo.client.datamodel_tables.find_one({'originalTableId': table_doc['_id'],
                                                           'datamodelId': g_datamodel_doc['_id']})
    if dm_table_doc is None:
        # datamodel_table for this table doesn't exist. inserting it
        new_dm_table = table_doc.copy()
        del new_dm_table['_id']
        new_dm_table['originalTableId'] = table_doc['_id']
        new_dm_table['datamodelId'] = g_datamodel_doc['_id']
        
        # check for transformations in config
        if g_dm_object.get('transformations'):
            if g_dm_object['transformations'].get(source) and g_dm_object['transformations'][source].get(table):
                new_dm_table['transform_rules'] = g_dm_object['transformations'][source][table]

        new_dm_table_id = mongo.client.datamodel_tables.insert(new_dm_table)

        print 'Inserted dm_table: "%s"' % new_dm_table_id
        return new_dm_table_id
    else:
        return dm_table_doc['_id']


def build_datamodel():
    params = {
        'datamodelId': str(g_datamodel_doc['_id']),
        'path': '/opt/infoworks/',
    }
    job = {
        'jobType': 'datamodel_build',
        'queueingStatus': 'queued',
        'entityIdStr': str(g_datamodel_doc['_id']),
        'entityType': 'datamodel',
        'status': 'pending',
        'params': params,
    }

    print 'Queueing datamodel build job.'
    meteor.client.call('submitJobWithStringId', [job], build_datamodel_callback)


def build_datamodel_callback(error, result):
    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    job_id = result
    print 'Queued job with id: ' + job_id
    mongo.client.datamodels.update({'_id': g_datamodel_doc['_id']}, {'$set': {'last_build_job': ObjectId(job_id)}})
    mongo.check_job_status(job_id, build_datamodel_done_callback)


def build_datamodel_done_callback(error, result):
    if error:
        misc.backround_process_terminate()
        return
    
    print 'Datamodel build completed.'
    meteor.ddp_call(validate_data)


def validate_data():
    global g_datamodel_doc

    params = {
        'entityType': 'datamodel',
        'entityId': str(g_datamodel_doc['_id']),
    }
    job = {
        'jobType': 'datamodel_validate',
        'queueingStatus': 'queued',
        'entityIdStr': str(g_datamodel_doc['_id']),
        'entityType': 'datamodel',
        'status': 'pending',
        'params': params,
    }

    print 'Queueing datamodel validation job.'
    if __debug__:
        print json.dumps(job)
    meteor.client.call('submitJobWithStringId', [job], validate_data_callback)


def validate_data_callback(error, result):
    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    job_id = result
    print 'Queued job with id: ' + job_id
    mongo.client.datamodels.update({'_id': g_datamodel_doc['_id']}, {'$set': {'last_validate_job': ObjectId(job_id)}})
    mongo.check_job_status(job_id, validate_data_done_callback)


def validate_data_done_callback(error, result):
    if error:
        misc.backround_process_terminate(True)
        return

    print 'Validating data of datamodel completed.'
    misc.backround_process_terminate(True)
    return


def check_cube():
    for cube in g_dm_object.get('cubes', []):
        global g_cube_object
        print '==============='
        print 'Starting automation script for cube: ' + cube['name']

        g_cube_object = mongo.client.cubes.find_one({'name': cube['name']})
        if not g_cube_object:
            print 'Creating cube.'
            g_cube_object = cube
            g_cube_object['datamodelId'] = get_dm_id(cube['datamodel'])
            del cube['datamodel']

            meteor.client.call('insertCube', [cube['name'], 'Test Cube', str(g_cube_object['datamodelId'])],
                               insert_cube_callback)
        else:
            print 'Cube exists.'
            cube['datamodelId'] = g_cube_object['datamodelId']
            cube['_id'] = g_cube_object['_id']
            del cube['datamodel']
            g_cube_object = cube

            design_cube()  # Update any change in the test configuration
            meteor.ddp_call(build_cube)
        misc.background_loop()


def get_dm_id(name):
    datamodel_doc = mongo.client.datamodels.find_one({'name': name}, {'_id': 1})
    return datamodel_doc['_id']


def get_dm_table_id(dm_id, table_name):
    table_doc = mongo.client.datamodel_tables.find_one({'datamodelId': dm_id, 'table': table_name}, {'_id': 1})
    return table_doc['_id']


def get_src_table_id(source_name, table_name):
    source_doc = mongo.client.sources.find_one({'name': source_name}, {'_id': 1})
    table_doc = mongo.client.tables.find_one({'source': source_doc['_id'], 'table': table_name}, {'_id': 1})
    return table_doc['_id']


def get_id_for_dimensions(dimensions):
    for dimension in dimensions:
        for attr in dimension['attrs']:
            if 'table' in attr:
                attr['tableId'] = get_src_table_id(attr['source'], attr['table'])
                del attr['table']
                del attr['source']
            else:
                attr['datamodelTableId'] = get_dm_table_id(g_cube_object['datamodelId'], attr['datamodelTable'])
                del attr['datamodel']
                del attr['datamodelTable']

        get_id_for_dimensions(dimension['dimensions'])


def insert_cube_callback(error, result):
    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    print 'Done!'

    g_cube_object['_id'] = ObjectId(result)
    design_cube()


def design_cube():
    for fact in g_cube_object['layout']['facts_table']['facts']:
        fact['datamodelTableId'] = get_dm_table_id(g_cube_object['datamodelId'], fact['datamodelTable'])
        del fact['datamodel']
        del fact['datamodelTable']
    get_id_for_dimensions(g_cube_object['layout']['dimensions'])

    print 'Designing cube.'
    mongo.client.cubes.update({'_id': g_cube_object['_id']}, {'$set': {
        'layout': g_cube_object['layout'],
        'hive_schema': g_cube_object['name'],
        'hdfs_path': '/datamodels/iw/' + g_cube_object['name']}
    })
    print 'Done!'

    meteor.ddp_call(build_cube)


def build_cube():
    params = {
        'cubeId': str(g_cube_object['_id']),
        'path': '/opt/infoworks/',
    }
    job = {
        'jobType': 'cube_build',
        'queueingStatus': 'queued',
        'entityIdStr': str(g_cube_object['_id']),
        'entityType': 'cube',
        'status': 'pending',
        'params': params,
    }

    print 'Queueing cube build job.'
    meteor.client.call('submitJobWithStringId', [job], build_cube_callback)


def build_cube_callback(error, result):
    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    job_id = result
    print 'Queued job with id: ' + job_id
    mongo.client.cubes.update({'_id': g_cube_object['_id']}, {'$set': {'last_build_job': ObjectId(job_id)}})
    mongo.check_job_status(job_id, build_cube_done_callback)


def build_cube_done_callback(error, result):
    if error:
        misc.backround_process_terminate()
        return

    print 'Cube build completed.'
    meteor.ddp_call(validate_cube)


def validate_cube():
    params = {
        'entityType': 'cube',
        'entityId': str(g_cube_object['_id']),
    }
    job = {
        'jobType': 'cube_validate',
        'queueingStatus': 'queued',
        'entityIdStr': str(g_cube_object['_id']),
        'entityType': 'cube',
        'status': 'pending',
        'params': params,
    }

    print 'Queueing cube validation job.'
    if __debug__:
        print json.dumps(job)
    meteor.client.call('submitJobWithStringId', [job], validate_cube_callback)


def validate_cube_callback(error, result):
    if error:
        print 'Error: ' + error
        misc.backround_process_terminate()
        return

    job_id = result
    print 'Queued job with id: ' + job_id
    mongo.client.cubes.update({'_id': g_cube_object['_id']}, {'$set': {'last_validate_job': ObjectId(job_id)}})
    mongo.check_job_status(job_id, validate_cube_done_callback)


def validate_cube_done_callback(error, result):
    if error:
        misc.backround_process_terminate()
        return

    print 'Validation of cube completed.'
    misc.backround_process_terminate(True)
    return


if __name__ == '__main__':
    main(sys.argv[1])
    sys.exit(misc.g_exit_code)
