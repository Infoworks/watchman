import sys
from utils import misc, cdc


def main(config_path):
    source_doc = cdc.get_source_doc(config_path)
    if not source_doc:
        misc.g_exit_code = 1
        return

    print 'Attempting to crawl the delta changes for source: ' + source_doc['name']

    params = {
        'source': str(source_doc['_id']),
        'schema': source_doc['connection']['schema'],
        'database': source_doc['connection']['database'],
        'driver': source_doc['connection']['driver_name'],
        'dns': source_doc['connection']['dns'],
        'private_key': source_doc['connection']['private_key'],
        'url': source_doc['connection']['connection_string'],
        'username': source_doc['connection']['username'],
        'password': source_doc['connection']['password']
    }
    cdc.do_job('source_cdc', source_doc['_id'], params)


if __name__ == '__main__':
    main(sys.argv[1])
    sys.exit(misc.g_exit_code)
