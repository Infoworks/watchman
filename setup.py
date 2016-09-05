import sys
import pip
import subprocess, os, stat
import ConfigParser

PY_VERSION_MAJOR = 2
PY_VERSION_MINOR = 7

PIP_PACKAGES = ['airflow', 'airflow[hive]', 'scriptine', 'sphinx', 'sphinx_rtd_theme'];

def main():
	try:
		if (not sys.version_info.major == PY_VERSION_MAJOR or not sys.version_info.minor == PY_VERSION_MINOR):
			print "Setup requires to be run using python version 2.7. Exiting setup."
			return 1
	except:
		print "Setup requires to be run using python version 2.7. Exiting setup."
		return 1

	print "Installing required packages using pip:"
	print "---------------------------------------"
	for p in PIP_PACKAGES:
		print "Installing: '%s'" % p
		pip.main(['install', p])
		print ''

	print "Initialising airflow database:"
	subprocess.call(['airflow', 'initdb'])

	#setup rosie
	print "\n"
	print "Configuring Rosie:"
	print "------------------"
	print "making scripts executable..."
	rosie_script_path_rel = '/watchman/scripts/rosie.py'
	rosie_script_path = os.getcwd() + rosie_script_path_rel
	current_stat = os.stat(rosie_script_path)
	os.chmod(rosie_script_path, current_stat.st_mode | stat.S_IEXEC)				# make rosie executable
	print "Done"

	# generate documentation locally
	print "\n"
	print "Generating documentation:"
	print "-------------------------"
	print "running docuemntation make commands..."
	doc_path = os.getcwd() + '/docs/'
	doc_path_index = doc_path+'_build/html/index.html'
	p = subprocess.Popen(['make', 'html'], cwd=doc_path)
	p.wait()
	print "Done."
	
	AIRFLOW_CORE_CFG_OVERWRITE = {
		'dags_folder': os.getcwd() + '/watchman/flows',
		'load_examples': 'False',
		'dags_are_paused_at_creation': 'False',
		'dags_are_paused_at_creation': 'False',
	}

	print "\n"
	print "Configuring Airflow:"
	print "--------------------"
	configure_airflow_default = 'yes'
	configure_airflow = raw_input('Configure Airflow? (This will modify Airflow configurations) Answer: yes or no. ['+configure_airflow_default+']: ')

	if (not configure_airflow):
		configure_airflow = configure_airflow_default

	if (configure_airflow == 'yes'):
		airflow_cfg_path_default = os.path.expanduser('~/airflow/airflow.cfg')
		airflow_cfg_path = raw_input('Path to airflow.cfg ['+airflow_cfg_path_default+']: ')
		if (not airflow_cfg_path):
			airflow_cfg_path = airflow_cfg_path_default

		airflow_webserver_port_default = '8080'
		airflow_webserver_port = raw_input('Airflow webserver port ['+airflow_webserver_port_default+']: ')
		if (not airflow_webserver_port):
			airflow_webserver_port = airflow_webserver_port_default

		print ""
		print "Overwriting some configs:"
		parser = ConfigParser.SafeConfigParser()
		try:
			parser.read(airflow_cfg_path)
			
			for k in AIRFLOW_CORE_CFG_OVERWRITE:
				print 'Setting [core][%s] to %s (previously: %s)' % (k, AIRFLOW_CORE_CFG_OVERWRITE[k], parser.get('core', k))
				parser.set('core', k, AIRFLOW_CORE_CFG_OVERWRITE[k])

			# overwrite [webserver] web_server_port
			parser.set('webserver', 'web_server_port', airflow_webserver_port)

			with open(airflow_cfg_path, 'w') as f:
				parser.write(f)
			print 'Done updating airflow configuration.'
		except Exception as e:
			print "Unable to read or write airflow config file"
			print e

	print "\n"
	print "SETUP COMPLETED SUCCESSFULLY!"
	
	
	# point to documentation
	# point to Rosie
	print "\n"
	print "Automation Documentation"
	print "========================"
	print "Visit: '%s' in your browser. " % doc_path_index
	print ""
	print "Rosie - the robot at your service."
	print "=================================="
	print "Rosie is a robot that will run flows and suits for you."
	print "For more details, issue the following command:"
	print "$ .%s -h" % rosie_script_path_rel
	print "\n"
	print "Have fun!"

main()