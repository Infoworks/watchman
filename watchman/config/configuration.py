import os

try:
    HOST = os.getenv('ROSIE_FLOW_IW_HOST')
except KeyError as e:
    HOST = '54.174.145.91'
    print 'Using "localhost" as the default IW HOST'

try:
    AUTH_TOKEN = os.getenv('ROSIE_FLOW_IW_USER_AUTH_TOKEN')
except KeyError as e:
    AUTH_TOKEN = 'dW5kZWZpbmVkOmFkbWluQGluZm93b3Jrcy5pbzoxMjM0NTY='
    print 'Using "admin@infoworks.io" as the default IW AUTH TOKEN'

REST_HOST = HOST
REST_PORT = '2999'
