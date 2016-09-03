#! /usr/bin/env python

import scriptine
import os
import subprocess
import time
from scriptine import path

FLOWS_DIR = 'flows'
DATASETS_DIR = 'datasets'
SUITES_DIR = 'suites'


def runflow_command(flow_name, dataset_name):
    """
    Executes a flow with a dataset

    :param flow_name: name of the flow to run
    :param dataset_name: name of the dataset to run the flow on
    """
    execution_status = False
    print 'Executing flow: "%s" with dataset: "%s"' % (flow_name, dataset_name)

    base_dir = path.cwd().parent

    flow_path = path(base_dir + '/' + FLOWS_DIR + '/' + flow_name + '.py')
    dataset_path = path(base_dir + '/' + DATASETS_DIR + '/' + flow_name + '/' + dataset_name)

    if not flow_path.exists():
        print "Flow file does not exist. Looking for file: %s" % flow_path
        return

    if not dataset_path.exists() or not dataset_path.isdir():
        print "Dataset directory does not exist. Looking for directory: %s" % dataset_path
        return

    custom_env = os.environ.copy()
    custom_env['ROSIE_FLOW_DATASET_BASE_PATH'] = dataset_path

    airflow_exec_cmd = 'airflow backfill {flow_name} -s {start_date}'.format(flow_name=flow_name,
                                                                             start_date=time.strftime("%Y-%m-%d"))

    process = subprocess.Popen(airflow_exec_cmd, shell=True, env=custom_env)
    process.communicate()
    if process.returncode == 0:
        execution_status = True
    print '**********************************'
    print 'Flow execution status: {status}'.format(status=execution_status)
    print '**********************************'


def runsuite_command(suite_name):
    """
    Executes a suite of flows

    :param suite_name: name of the suite to run
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
        runflow_command(tokens[0], tokens[1])
        print ''


def list_command(entity_type, with_datasets=False):
    """
    Lists flows and suites

    :param entity_type: entity_type you would like to list (choices: 'suites', 'flows')
    :param with_datasets: list flows with available datasets (only applicable for entity_type=flows)
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

if __name__ == '__main__':
    scriptine.run()
