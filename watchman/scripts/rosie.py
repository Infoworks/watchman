#! /usr/bin/env python

import scriptine
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
	print 'Executing flow: "%s" with dataset: "%s"' % (flow_name, dataset_name)

	base_dir = path.cwd().parent

	flow_path = path(base_dir + '/' + FLOWS_DIR + '/' + flow_name+'.py')
	dataset_path = path(base_dir + '/' + DATASETS_DIR + '/' + flow_name + '/' + dataset_name)

	if (not flow_path.exists()):
		print "Flow file does not exist. Looking for file: %s" % flow_path
		return

	if (not dataset_path.exists() or not dataset_path.isdir()) :
		print "Dataset directory does not exist. Looking for directory: %s" % dataset_path
		return

	# TODO: trigger subprocess with the following details and then remove these print statements
	print "Starting execution of flow: %s with dataset %s" % (flow_name, dataset_name);
	print 'Set ENV VAR: ROSIE_FLOW_DATASET_BASE_PATH: ', dataset_path
	print 'Execute flow: ', flow_path
	print '...'
	print 'Returned from flow script with response: SUCCESS'

def runsuite_command(suite_name):
	"""
	Executes a suite of flows

    :param suite_name: name of the suite to run
	"""
	print 'Executing all flows in suite: %s' % suite_name

	base_dir = path.cwd().parent

	suite_path = path(base_dir + '/' + SUITES_DIR + '/' + suite_name)

	if (not suite_path.exists()):
		print "Suite file does not exist. Looking for file in path: %s" % suite_path
		return

	suite_commands = suite_path.lines()
	if (not len(suite_commands)):
		print "Suite file does not contain any commands."
		return

	for line in suite_commands:
		tokens = line.strip().split("\t")
		runflow_command(tokens[0], tokens[1])
		print ''

def list_command(entity, with_datasets=False):
	"""
	Lists flows and suites

	:param entity: entity you would like to list (choices: 'suites', 'flows')
	:param with_datasets: (only applicable for entity=flows)
	"""

	ignored_files = ['.DS_Store', '__init__']

	base_dir = path.cwd().parent

	entries = []
	print "List of %s" % entity
	print "--------------------"
	if (entity == 'flows'):
		entity_path = path(base_dir + '/' + FLOWS_DIR)
		if (entity_path.exists()):
			entries = entity_path.files()
	elif (entity == 'suites'):
		entity_path = path(base_dir + '/' + SUITES_DIR)
		if (entity_path.exists()):
			entries = entity_path.files()

	entry_names = set([])
	for e in entries:
		namebase = e.namebase
		if (not namebase in ignored_files):
			entry_names.add(namebase)

	for e in entry_names:
		print e

if __name__ == '__main__':
	scriptine.run()