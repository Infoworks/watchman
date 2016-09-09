import os
import sys
import json
import logging


def load_json_config(path_to_file, stringify=True):
    try:
        if not os.path.isfile(path_to_file):
            logging.error('Path to file is incorrect. Please check the existence of {path}'.format(path=path_to_file))
            sys.exit(1)
        with open(path_to_file, 'r') as json_file:
            if stringify:
                return json_file.read().replace('\n', '')
            else:
                return json.load(json_file)
    except Exception as e:
        logging.error('Exception: ' + str(e))
        logging.error('Error occurrred while trying to read the config file.')
        sys.exit(1)
