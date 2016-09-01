import sys
import jpype
import jaydebeapi
from os import path
from utils import misc, cdc
import json


jar_location = {
    'ORACLE': ['/opt/infoworks/lib/oracle-jdbc-driver/ojdbc6.jar'],
    'TERADATA': ['/opt/infoworks/lib/teradata/terajdbc4.jar', '/opt/infoworks/lib/teradata/tdgssconfig.jar']
}
oracle_sysdba_password = 'iworacle12'


def main(config_path):
    source_doc = cdc.get_source_doc(config_path)
    if not source_doc:
        misc.g_exit_code = 1
        return

    with open(config_path, 'r') as config_file:
        config = json.loads(config_file.read())['config']
        sql_script_path = config.get('sql_script_path')
        repeat = config.get('repeat', 1)
    if not sql_script_path:
        print 'SQL script missing from configuration'
        misc.g_exit_code = 1
        return
    sql_script_path = path.join(path.dirname(config_path), sql_script_path)

    print 'Attempting to modify source: ' + source_doc['name']

    try:
        connection = source_doc['connection']
        database = connection['database']
        connection_string = connection['connection_string']

        jpype.startJVM(jpype.getDefaultJVMPath(), '-Djava.class.path={jar_location}'.format(
            jar_location=':'.join(jar_location[database])))
        conn = jaydebeapi.connect(connection['driver_name'],
                                  [connection_string, connection['username'], connection['password'].decode('base64')],
                                  jar_location[database])
        cursor = conn.cursor()
    except Exception as e:
        print e.message
        print 'DB connection failure!'
        misc.g_exit_code = 1
        return

    query_count = 0
    with open(sql_script_path, 'r') as f:
        for row in f:
            if len(row) < 2:  # Empty line
                continue
            end = row.find(';')
            if end != -1:
                row = row[:end]
            cursor.executemany(row, [() for _ in range(repeat)])

            query_count += 1
    conn.commit()
    conn.close()
    print str(query_count) + ' queries executed successfully.'

    if database == 'ORACLE':
        # Immediately push the binlogs
        conn = jaydebeapi.connect(connection['driver_name'],
                                  [connection_string, 'sys as sysdba', oracle_sysdba_password],
                                  jar_location[database])
        cursor = conn.cursor()
        cursor.execute('alter system switch logfile')
        conn.commit()
        conn.close()

if __name__ == '__main__':
    main(sys.argv[1])
    sys.exit(misc.g_exit_code)
