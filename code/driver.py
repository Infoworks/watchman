import sys
import fcntl
import os
import json
import select
import shlex
import subprocess
from time import time
from StringIO import StringIO

cases = {}
tests_succeeded = []
tests_failed = []


class TestsRunner(object):
    def __init__(self, chain):
        self._poll = select.poll()
        self._chain = chain

    def run(self):
        test_processes = {}
        for test in self._chain:
            args = self.get_test_arg(test)
            if not args:
                continue

            args.append(test)
            test_process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            test_process.is_positive = cases[test].get('testType', 'positive') == 'positive'
            test_process.name = '[%s]' % cases[test]['name']
            test_process.start_time = time()
            test_process.io_buffer = StringIO()

            pipe_fd = test_process.stdout.fileno()
            fcntl.fcntl(pipe_fd, fcntl.F_SETFL, fcntl.fcntl(pipe_fd, fcntl.F_GETFL) | os.O_NONBLOCK)
            test_processes[pipe_fd] = test_process
            self._poll.register(pipe_fd)

        # Poll processes
        while test_processes:
            for reports in self._poll.poll():
                test_process = test_processes[reports[0]]
                self.drain_pipe(test_process)
                if reports[1] != select.POLLHUP:  # Child has terminated
                    continue
                if test_process.poll() is None:  # Exit code is not yet available
                    continue

                test_summary = '%ds\t%s' % (int(time() - test_process.start_time), test_process.name)
                if test_process.poll() != 0 and test_process.is_positive:
                    tests_failed.append(test_summary)
                else:
                    tests_succeeded.append(test_summary)

                output = test_process.io_buffer.getvalue()
                if output:
                    print '==============='
                    print output
                    print '==============='

                del test_processes[reports[0]]
                self._poll.unregister(reports[0])

    @staticmethod
    def drain_pipe(process):
        try:
            i = process.stdout.read(4096)
            while i:
                process.io_buffer.write(i)
                i = process.stdout.read(4096)
        except IOError:
            pass

        if sys.stdout.isatty():  # Are we on a terminal?
            process.io_buffer.seek(0)
            i = process.io_buffer.readline()
            while i:
                if i[-1] == '\n':
                    sys.stdout.write(process.name)
                    sys.stdout.write(' ')
                    sys.stdout.write(i)
                else:
                    print process.name, i
                i = process.io_buffer.readline()
            process.io_buffer.truncate(0)

    @staticmethod
    def get_python_command(script):
        if sys.flags.optimize:
            return [sys.executable, '-O', '-u', script]
        return [sys.executable, '-u', script]

    @staticmethod
    def get_test_arg(test):
        entity_type = cases[test].get('entityType', '(null)')
        if entity_type == 'source':
            return TestsRunner.get_python_command('source.py')
        elif entity_type == 'datamodel':
            return TestsRunner.get_python_command('datamodel.py')
        elif entity_type == 'source_rdbms_modify':
            return TestsRunner.get_python_command('cdc_sql_script.py')
        elif entity_type == 'source_cdc_fetch_delta':
            return TestsRunner.get_python_command('cdc_fetch_delta.py')
        elif entity_type == 'source_cdc_merge_delta':
            return TestsRunner.get_python_command('cdc_merge_delta.py')
        elif entity_type == 'scd_crawl':
            return TestsRunner.get_python_command('scd_crawl.py')
        elif entity_type == 'scd_build':
            return TestsRunner.get_python_command('scd_build.py')
        elif entity_type == 'scd_delete':
            return TestsRunner.get_python_command('scd_delete.py')
        elif entity_type == 'shell':
            return shlex.split(cases[test]['config']['script'])
        else:
            print 'Unknown entity type %s in test %s' % (entity_type, test)


def main():
    suite = sys.argv[1]
    try:
        tests = os.listdir(suite)
        tests.sort()
    except Exception:
        print 'Unable to find test cases in ' + suite
        return

    if not tests:
        print 'No test case objects found in ' + suite
        return

    chains = [[]]
    test_dependencies = []
    for test in tests:
        test_name = os.path.splitext(test)[0]
        test = os.path.join(suite, test)
        try:
            with open(test, 'r') as config_file:
                cases[test] = json.load(config_file)
        except Exception:
            print 'Invalid test object ' + test
            continue

        if 'name' not in cases[test]:
            cases[test]['name'] = test_name
        dependencies = cases[test].get('dependsOn', None)
        if dependencies:
            for dependency in dependencies:
                test_dependencies.append((os.path.join(suite, dependency), test))
        else:
            chains[0].append(test)

    while test_dependencies:
        test_dependencies = [edge for edge in test_dependencies if insert(edge, chains)]

    for chain in chains:
        TestsRunner(chain).run()

    tests_succeeded.insert(0, '%d test(s) succeeded:' % len(tests_succeeded))
    tests_failed.insert(0, '%d test(s) failed' % len(tests_failed))
    print '==============='
    print 'Summary:'
    print '\n\t'.join(tests_succeeded)
    print '\n\t'.join(tests_failed)
    print '==============='

    if len(tests_failed) > 0:
        sys.exit(1)


def insert(edge, chains):
    found = [False, False]

    # Find the position of where the edge[0] needs to be inserted, if it needs to
    insert_position = 0
    for i in range(len(chains)):
        if edge[0] in chains[i]:
            found[0] = True
            insert_position = i
            break
    if not found[0]:
        chains[insert_position].append(edge[0])

    insert_position += 1
    # Remove edge[1] from one of the lower chains (compared to edge[1])
    for i in range(min(insert_position, len(chains))):
        if edge[1] in chains[i]:
            found[1] = True
            chains[i].remove(edge[1])
            break

    # Extend the chains if required
    if len(chains) <= insert_position:
        chains.append([])

    # Insert edge[1] in the appropriate chain
    if found[1]:
        chains[insert_position].append(edge[1])
    else:
        for i in range(insert_position, len(chains)):
            if edge[1] in chains[i]:
                found[1] = True
                break
        if not found[1]:
            chains[insert_position].append(edge[1])

    if found[0] and found[1]:
        return False
    return True

main()
