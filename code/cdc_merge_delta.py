import sys
from utils import misc, cdc


def main(config_path):
    source_doc = cdc.get_source_doc(config_path)
    if not source_doc:
        misc.g_exit_code = 1
        return

    print 'Attempting to merge the delta changes for source: ' + source_doc['name']

    params = {
        'source': str(source_doc['_id']),
        'tables': [{'_id': {'$type': 'oid', '$value': str(i)}} for i in source_doc['tables']],
    }
    cdc.do_job('source_merge', source_doc['_id'], params)

if __name__ == '__main__':
    main(sys.argv[1])
    sys.exit(misc.g_exit_code)
