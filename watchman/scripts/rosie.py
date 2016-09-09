#! /usr/bin/env python

"""Rosie is a robot that can execute a flow or a suite of flows based on your command.
"""

import scriptine
import os
import signal
import subprocess
import time
import sys
import importlib
import re
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

    if not _validate_flow_and_dataset(flow_name=flow_name, flow_path=flow_path, dataset_path=dataset_path):
        return 1
    else:
        print "Flow file validated successfully."

    # check_airflow_services_command(True)
    webserver_command(start=True)
    scheduler_command(start=True)

    run_id = 'rosie_{date_formatted}'.format(date_formatted=time.strftime("%Y-%m-%d-%H-%M-%S"))
    custom_env = os.environ.copy()
    custom_env['ROSIE_FLOW_DATASET_BASE_PATH'] = dataset_path.abspath()
    if iw_host is not None:
        custom_env['ROSIE_FLOW_IW_HOST'] = iw_host
    if iw_user_at is not None:
        custom_env['ROSIE_FLOW_IW_USER_AUTH_TOKEN'] = iw_user_at

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


def validate_flow_and_dataset(flow_name, flow_path, dataset_path):
    # check that the flow file exists
    if not flow_path.exists():
        print "Flow file does not exist. Looking for file: %s" % flow_path
        return False

    # check that the dag file compiles
    try:
        sys.path.insert(0, flow_path.parent)
        importlib.import_module(flow_name)
    except Exception as e:
        print "\nError found:"
        print "------------"
        print "Flow file contains errors. Please fix them and try again."
        print str(e)
        return False

    # check that the flow name and the dag name match
    pattern = re.compile("DAG\s*\(\s*[\"|']" + flow_name + "[\"|']")
    file_text = flow_path.text()

    found = pattern.search(file_text)
    if not found:
        print "\nError found:"
        print "------------"
        print "The DAG name has to be the same as the file name. Please fix it and try again."
        print "Suggestion: set the dag name to: ", flow_name
        return False

    if not dataset_path.exists() or not dataset_path.isdir():
        print "\nError found:"
        print "------------"
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


def flows_command(datasets=False):
    """
    Lists flows

    :param datasets: list flows with available datasets
    :type datasets: boolean
    """

    ignored_files = ['.DS_Store', '__init__']

    base_dir = path.cwd().parent

    entries = []
    print "List of flows:"
    print "--------------"
    entity_path = path(base_dir + '/' + FLOWS_DIR)
    if entity_path.exists():
        entries = entity_path.files()

    entry_names = set([])
    for e in entries:
        namebase = e.namebase
        if not namebase in ignored_files:
            if datasets:
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

def suites_command():
    """
    Lists suites
    """

    ignored_files = ['.DS_Store', '__init__']

    base_dir = path.cwd().parent

    entries = []
    print "List of suites:"
    print "---------------"
    entity_path = path(base_dir + '/' + SUITES_DIR)
    if entity_path.exists():
        entries = entity_path.files()

    entry_names = set([])
    for e in entries:
        namebase = e.namebase
        if not namebase in ignored_files:
            entry_names.add(namebase)

    for e in sorted(entry_names):
        print e


def webserver_command(start=False, stop=False, restart=False):
    """
    Webserver (from Airflow) service. Pass start, stop or restart to perform an action.

    :param start: start webserver
    :param stop: stop webserver
    :param restart: restart webserver
    :type start: boolean
    :type stop: boolean
    :type restart: boolean
    :returns: True if webserver is running, False otherwise
    :rtype: boolean
    """
    return _service_command('webserver', start, stop, restart)


def scheduler_command(start=False, stop=False, restart=False):
    """
    Scheduler (from Airflow) service. Pass start, stop or restart to perform an action.

    :param start: start scheduler
    :param stop: stop scheduler
    :param restart: restart scheduler
    :type start: boolean
    :type stop: boolean
    :type restart: boolean
    :returns: True if scheduler is running, False otherwise
    :rtype: boolean
    """
    return _service_command('scheduler', start, stop, restart)


def _service_command(service, start=False, stop=False, restart=False):
    service_pid = _service_is_running(service)

    option_passed = False
    if stop:
        option_passed = True

        if service_pid:
            os.kill(service_pid, signal.SIGTERM)
            print "{service} stopped.".format(service=service)
            return True
        else:
            print "{service} is not running".format(service=service)
            return False

    if start:
        option_passed = True
        if service_pid:
            print "{service} is already running. (PID = {pid})".format(service=service, pid=service_pid)
            return True
        else:
            _start_process(service)
            print "{service} started.".format(service=service)
            return True

    if restart:
        option_passed = True
        _service_command(service, stop=True)
        time.sleep(3)
        _service_command(service, start=True)

    if not option_passed:
        if service_pid:
            print "{service} is running. (PID = {pid})".format(service=service, pid=service_pid)
            return True
        else:
            print "{service} is not running".format(service=service)
            return False


def _service_is_running(service):
    # check for the airflow-webserver.pid file in airflow home directory.
    airflow_base_path = '~/airflow/'

    if service == 'webserver':
        service_file = 'airflow-webserver.pid'
    elif service == 'scheduler':
        service_file = 'airflow-scheduler.pid'

    # TODO: allow user to set an env var with a different airflow conf directory if needed
    
    pid_file_path = path(airflow_base_path + service_file).expanduser()

    if pid_file_path.exists():
        pid = int(pid_file_path.text().strip())
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return pid
    else:
        return False


def _validate_flow_and_dataset(flow_name, flow_path, dataset_path):
    # check that the flow file exists
    if not flow_path.exists():
        print "Flow file does not exist. Looking for file: %s" % flow_path
        return False

    # check that the dag file compiles
    try:
        sys.path.insert(0, flow_path.parent)
        importlib.import_module(flow_name)
    except Exception as e:
        print "Flow file contains errors. Please fix them and try again."
        print "---------------------------------------------------------"
        print str(e)
        return False

    # check that the flow name and the dag name match


    if not dataset_path.exists() or not dataset_path.isdir():
        print "Dataset directory does not exist. Looking for directory: %s" % dataset_path
        return False

    return True


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
