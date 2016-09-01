from pymongo import MongoClient
import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config.configuration import *
host = HOST
port = PORT
mongo_username = MONGO_USERNAME
mongo_password = MONGO_PASSWORD
mongo_db = MONGO_DB

try:

    host_base_url = 'mongodb://{user_name}:{password}@{ip}:{port}/{db}'.format(user_name=mongo_username,
                                                                               password=mongo_password,
                                                                               ip=host, port=port, db=mongo_db)
    mongodb = MongoClient(host=host_base_url)[mongo_db]
    print 'MongoDB connection successful.'

except Exception as e:
    print 'MongoDB connection failure.'
    print e.message
    raise

