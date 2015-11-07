from MeteorClient import MeteorClient
from misc import g_host_address
import ejson

# Disable escaping any ejson types since we use ObjectIds everywhere
# https://www.meteor.com/ejson
ejson.EJSON_KEYWORDS = ()

client = None
callback_function = None


def connect():
    global client
    if client:
        return

    client = MeteorClient('ws://%s:3000/websocket' % g_host_address)
    client.on('logged_in', logged_in)  # will be called after re-connecting too!
    client.connect()


def login_callback(error, _=None):
    if error:
        print error['message']
    else:
        if __debug__:
            print 'Logged in to meteor'

        global callback_function
        if callback_function:
            callback_function()
            callback_function = None


def logged_in(data):
    login_callback(None, data)


def ddp_call(cb):
    # We have to create a call to login even if already logged in because
    # the connection would have broken.
    global callback_function
    callback_function = cb
    client.login('admin@infoworks.io', '123456', callback=login_callback)
