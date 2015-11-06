from pymongo import MongoClient
from bson import ObjectId
from subprocess import check_output
from misc import g_host_address
import time

client = MongoClient('mongodb://infoworks:IN11**rk@%s:27017/infoworks-new' % g_host_address)['infoworks-new']
job_name = ''


def check_job_status(job_id, callback, sleep_duration=1):
    previous_status = ''
    print_count = 0
    while True:
        job_doc = client.jobs.find_one({'_id': ObjectId(job_id)})
        if job_doc:
            if job_doc['status'] == 'completed':
                print '%s %s (%s) - done!' % (job_doc['jobType'], job_doc['entityId'], job_id)
                break
            elif job_doc['status'] == 'canceled':
                print '%s %s (%s) - canceled!' % (job_doc['jobType'], job_doc['entityId'], job_id)
                callback('job failed', None)
                return
            elif job_doc['status'] == 'failed' or job_doc['queueingStatus'] in ('blocked', 'dequeued'):
                print '==============='
                print 'Job %s of %s failed! To track the error, go to:' % (job_doc['jobType'], job_name)
                print 'http://%s:3000/admin/%s' % (
                    check_output(['curl', '-s', 'http://169.254.169.254/latest/meta-data/public-ipv4']),
                    'job_queue' if job_doc['queueingStatus'] == 'blocked' else 'job_logs?jobId=' + job_id
                )
                print '==============='

                callback('job failed', None)
                return
            else:
                if type(job_doc.get('percentCompleted')) is float:
                    current_status = '%s %s (%s) - %.2f%%' % (job_doc['jobType'], job_doc['entityId'],
                                                              job_id, job_doc['percentCompleted'])
                else:
                    current_status = '%s %s (%s) - running...' % (job_doc['jobType'], job_doc['entityId'], job_id)
                if current_status == previous_status:
                    if print_count % 10 == 0:
                        print_count = 1
                        print current_status
                    else:
                        print_count += 1
                else:
                    previous_status = current_status
                    print current_status
        time.sleep(sleep_duration)

    callback(None, job_id)
