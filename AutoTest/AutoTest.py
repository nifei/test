__author__ = 'test'
import time
import MySQLdb

def autoTest():
    query_action(1)

def run_sync(device_id, script):
    (action_id, status) = insert_action(device_id, "EXECUTE", script)
    while status == 'PENDING' or status == 'RUNNING' or status == None:
        status = query_action(action_id);
        print "script: %s status: %s" %(script, status)
        time.sleep(1)
    return action_id, status

def run_async(device_id, script):
    (action_id, status) = insert_action(device_id, "EXECUTE", script)
    return action_id

def wait(action_id):
    status = 'INIT'
    while status == 'PENDING' or status == 'RUNNING' or status == None:
        status = query_action(action_id)
        time.sleep(1)
    return status

# DeviceAction
# ID | Action | File | Status | MAC
# Database
host = 'localhost'
user = 'root'
password = '123456'
dbname = 'P2PDevice'
def query_action(action_id):
   # return status in ('Pending', 'Running')
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("select * from DeviceAction where ID='%s'" % action_id)
    print cursor.fetchone()
    db.close()
    pass

def insert_action(device_id, action, script):
    return (0, 'PENDING')
    # return action_id,'PENDING'

def update_action_status(action_id, status):
    pass
    # return

autoTest()
