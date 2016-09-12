import ast
import time
import requests
import logging
import os,sys,inspect
import subprocess

"""
 executes a sql query (TODO- As of now underlying java code only supports
"""
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def qry_rdbms(db_conf_path, sqlQuery):
    try:
        if (not db_conf_path) or (not sqlQuery):
            logging.error('DB configuration path or sql query has not been specified. ')
            sys.exit(1)
        if not os.path.isfile(db_conf_path):
            logging.error('Path to DB config file is incorrect. '
                          'Please check the existence of {path}'.format(path=db_conf_path))
            sys.exit(1)

        jar_command = 'java -cp {parent_dir}/utils/AutomationUtils.jar:{parent_dir}/utils/jars/* ' \
                      'io.infoworks.sql.SqlExecutor -dbConf {db_conf_path} -sql ' \
                      '{sql_query}'.format(parent_dir=parent_dir,
                                                 db_conf_path=db_conf_path,
                                                 sql_query=sqlQuery)

        logging.info('Jar command to be executed for sql query execution is : ' + jar_command)
        process = subprocess.Popen(jar_command, shell=True, stdout=subprocess.PIPE)
        stdoutdata, stderrdata = process.communicate()
	
	return stdoutdata 

    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Error occurred while trying to execute sql.')
        sys.exit(1)

print(qry_rdbms('/Users/sandeepkhurana/misc/db.conf', '\"select count{star} from customers\"'.format(star='(*)')))
