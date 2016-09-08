#! /usr/bin/env python

"""Rosie is a robot that can execute a flow or a suite of flows based on your command.
"""

import scriptine
import os
import subprocess
import time
import py_compile
from scriptine import path

FLOWS_DIR = 'flows'
DATASETS_DIR = 'datasets'
SUITES_DIR = 'suites'


def runflow_command(flow_name, dataset_name, iw_host=None, iw_user_at=None):
    """
    Executes a flow with a dataset

    :param flow_name: name of the flow to run
    :type flow_name: string
    :param dataset_name: name of the dataset to run the flow on
    :type dataset_name: string
    :param iw_host: hostname (or IP address) of the Infoworks REST API service. (eg: 127.0.0.1)
    :type iw_host: string
    :param iw_user_at: User authentication token to submit requests to the Infoworks REST API
    :type iw_user_at: string
    :returns: Execution status of the flow
    :rtype: boolean
    """
    execution_status = False
    print 'Executing flow: "%s" with dataset: "%s"' % (flow_name, dataset_name)

    base_dir = path.cwd().parent

    flow_path = path(base_dir + '/' + FLOWS_DIR + '/' + flow_name + '.py')
    dataset_path = path(base_dir + '/' + DATASETS_DIR + '/' + flow_name + '/' + dataset_name)

    if (not validate_flow_and_dataset(flow_path, dataset_path)):
        return 1
    else:
        print "Flow file validated successfully."

    check_airflow_services_command(True)

    run_id = '{flow_name}_{date_formatted}'.format(flow_name=flow_name,
                                                   date_formatted=time.strftime("%Y-%m-%d-%H-%M-%S"))
    custom_env = os.environ.copy()
    custom_env['ROSIE_FLOW_DATASET_BASE_PATH'] = dataset_path
    if iw_host is not None:
        custom_env['ROSIE_FLOW_IW_HOST'] = iw_host
    if iw_user_at is not None:
        custom_env['ROSIE_FLOW_IW_USER_AUTH_TOKEN'] = iw_user_at

    # airflow_exec_cmd = 'airflow backfill {flow_name} -s {start_date}'.format(flow_name=flow_name,
    #                                                                        start_date=time.strftime("%Y-%m-%d"))

    airflow_exec_cmd = 'airflow trigger_dag {flow_name} -r {run_id}'.format(flow_name=flow_name, run_id=run_id)

    print ""
    print "Command: %s" % airflow_exec_cmd
    process = subprocess.Popen(airflow_exec_cmd, shell=True, env=custom_env)
    process.communicate()
    if process.returncode == 0:
        execution_status = True
    print '**********************************'
    print 'Flow Run ID: ', run_id
    print 'Flow execution status: {status}'.format(status=execution_status)
    print '**********************************'

    return execution_status


def validate_flow_and_dataset(flow_path, dataset_path):
    # check that the flow file exists
    if not flow_path.exists():
        print "Flow file does not exist. Looking for file: %s" % flow_path
        return False
    """
    # check that the dag file compiles
    try:
        comp = py_compile.compile(flow_path, doraise=True)
        print 'comp'
        print comp
    except Exception as e:
        print "Flow file contains errors:"
        print e
        return False
    """

    # check that the flow name and the dag name match

    if not dataset_path.exists() or not dataset_path.isdir():
        print "Dataset directory does not exist. Looking for directory: %s" % dataset_path
        return False

    return True


def runsuite_command(suite_name, iw_host='localhost', iw_user_auth_token=''):
    """
    Executes a suite of flows. This command iterates over the flows in the suite file and sequentially calls :func:`runflow_command`.

    :param suite_name: name of the suite to run
    :type suite_name: string
    :param iw_host: hostname (or IP address) of the Infoworks REST API service
    :type iw_host: string
    :param iw_user_auth_token: User authentication token to submit requests to the Infoworks REST API
    :type iw_user_auth_token: string
    :returns: Execution status of the suite (True of all flows succeeded, False otherwise)
    :rtype: boolean

    .. note::
       All flows will be executed sequentially, even if one or more flows fail.

    """
    print 'Executing all flows in suite: %s' % suite_name

    base_dir = path.cwd().parent

    suite_path = path(base_dir + '/' + SUITES_DIR + '/' + suite_name)

    if not suite_path.exists():
        print "Suite file does not exist. Looking for file in path: %s" % suite_path
        return

    suite_commands = suite_path.lines()
    if not len(suite_commands):
        print "Suite file does not contain any commands."
        return

    for line in suite_commands:
        tokens = line.strip().split("\t")
        runflow_command(tokens[0], tokens[1], iw_host, iw_user_auth_token)
        print ''


def list_command(entity_type, with_datasets=False):
    """
    Lists flows and suites

    :param entity_type: entity_type you would like to list (choices: 'suites', 'flows')
    :type entity_type: string
    :param with_datasets: list flows with available datasets (only applicable for entity_type=flows)
    :type with_datasets: boolean
    """

    ignored_files = ['.DS_Store', '__init__']

    base_dir = path.cwd().parent

    entries = []
    print "List of %s" % entity_type
    print "--------------------"
    if entity_type == 'flows':
        entity_path = path(base_dir + '/' + FLOWS_DIR)
        if entity_path.exists():
            entries = entity_path.files()
    elif entity_type == 'suites':
        entity_path = path(base_dir + '/' + SUITES_DIR)
        if entity_path.exists():
            entries = entity_path.files()

    entry_names = set([])
    for e in entries:
        namebase = e.namebase
        if not namebase in ignored_files:
            if entity_type == 'flows' and with_datasets:
                datasets_dir = path(base_dir + '/' + DATASETS_DIR + '/' + namebase)
                if datasets_dir.exists():
                    for ds in datasets_dir.dirs():
                        entry_names.add(namebase + ' ' + ds.namebase)
                else:
                    entry_names.add(namebase)
            else:
                entry_names.add(namebase)

    for e in sorted(entry_names):
        print e


def check_airflow_services_command(start_if_down=True):
    """
    Checks if the required Airflow services are running (currently checks for scheduler and webserver).

    :param start_if_down: set to True if the services should be started up if they are down
    :type start_if_down: boolean
    """
    proc_scheduler = 'airflow scheduler'
    proc_webserver = 'airflow-webserver'

    # check scheduler
    if not _ps_aux_grep(proc_scheduler):
        print "Airflow scheduler is not running."
        if start_if_down:
            print "Starting airflow scheduler..."
            _start_process('scheduler')

    # check webserver
    if not _ps_aux_grep(proc_webserver):
        print "Airflow webserver is not running."
        if start_if_down:
            print "Starting airflow webserver..."
            _start_process('webserver')

    return


def _ps_aux_grep(proc_string):
    """
    Executes a `ps aux | grep $proc_string` command to see if the service is running

    :param proc_string: process string to grep for (in `ps aux` output)
    :type proc_string: string
    :returns: True if the process is running, False otherwise
    :rtype: boolean
    """
    p1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', proc_string], stdin=p1.stdout, stdout=subprocess.PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output_list = p2.communicate()[0].strip().split('\n')
    return len(output_list) > 1


def _start_process(proc_name):
    """
    Starts the airflow process

    :param proc_name: name of the airflow process to start
    :type proc_name: string
    """
    cmd = ''
    if proc_name == 'scheduler':
        cmd = 'airflow scheduler -D'
    elif proc_name == 'webserver':
        cmd = 'airflow webserver -D'

    cmd_list = cmd.split(' ')
    process = subprocess.Popen(cmd_list)
    process.communicate()


if __name__ == '__main__':
    scriptine.run()
