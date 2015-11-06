import json
import re
import time

g_host_address = '127.0.0.1'
g_terminate_bg_process = False
g_exit_code = 0



def replace_place_holders(template, replacements):
    # json.dumps encloses the string in quotes
    rep = dict((re.escape(k), json.dumps(v)[1:-1]) for k, v in replacements.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    return pattern.sub(lambda m: rep[re.escape(m.group(0))], template)


def background_loop():
    global g_terminate_bg_process

    # (sort of) hacky way to keep the client alive
    # ctrl + c to kill the script
    while True:
        if g_terminate_bg_process is True:
            break
        time.sleep(1)
    g_terminate_bg_process = False  # reset it in case there is another job


def backround_process_terminate(success=False):
    global g_terminate_bg_process, g_exit_code
    g_terminate_bg_process = True
    g_exit_code = 0 if success else 1
