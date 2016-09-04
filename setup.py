import sys
import pip
import subprocess, os, stat

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
	for p in PIP_PACKAGES:
		print "Installing: '%s'" % p
		pip.main(['install', p])
		print ''

	print "Initialising airflow database:"
	subprocess.call(['airflow', 'initdb'])

	#setup rosie
	print "\n"
	print "Configuring rosie..."
	rosie_script_path_rel = '/watchman/scripts/rosie.py'
	rosie_script_path = os.getcwd() + rosie_script_path_rel
	current_stat = os.stat(rosie_script_path)
	os.chmod(rosie_script_path, current_stat.st_mode | stat.S_IEXEC)				# make rosie executable
	print "Done"

	# generate documentation locally
	print "\n"
	print "Generating documentation..."
	doc_path = os.getcwd() + '/docs/'
	doc_path_index = doc_path+'_build/html/index.html'
	p = subprocess.Popen(['make', 'html'], cwd=doc_path)
	p.wait()
	print "Done."

	print "\n"
	print "Setup completed successfully."

	# point to documentation
	# point to Rosie
	print "\n"
	print "Automation Documentation"
	print "========================"
	print "Visit: '%s' in your browser. " % doc_path_index
	print "\n"
	print "Rosie - the robot at your service."
	print "=================================="
	print "Rosie is a robot that will run flows and suits for you."
	print "For more details, issue the following command:"
	print "$ .%s -h" % rosie_script_path_rel
	print "\n"
	print "Have fun!"


main()