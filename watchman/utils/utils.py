import json
import os
import sys


def load_json_config(path_to_file):
    try:
        if not os.path.isfile(path_to_file):
            print 'Path to file is incorrect. Please check the existence of {path}'.format(path=path_to_file)
            sys.exit(1)
        with open(path_to_file, 'r') as json_file:
            return json_file.read().replace('\n', '')
    except Exception as e:
        print 'Exception: ', e
        print 'Error occurrred while trying to read the file.'
        sys.exit(1)
