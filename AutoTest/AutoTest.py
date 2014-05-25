__author__ = 'test'
import time
import MySQLdb

def autoTest():
    action_3 = deploy_async(1, 'download/3.sh')
    print "action id:%s, status:%s" % (action_3, wait(action_3))
    action_4,status = run_sync(1, 'download/3.sh')
    print "action id:%s, status:%s" % (action_4, status)

def run_sync(device_id, script):
    return action_sync(device_id, "EXECUTE", script)

def run_async(device_id, script):
    return action_async(device_id, "EXECUTE", script)

def deploy_sync(device_id, script):
    return action_sync(device_id, "GET", script)

def deploy_async(device_id, script):
    return action_async(device_id, "GET", script)

def action_sync(device_id, action, script):
    action_id = insert_action(device_id, action, script)
    status = 'PENDING'
    while status == 'PENDING' or status == 'RUNNING':
        status = query_action_status(action_id);
        time.sleep(1)
    return action_id, status

def action_async(device_id, action, script):
    action_id = insert_action(device_id, action, script)
    return action_id

def wait(action_id):
    status = query_action_status(action_id)
    while status == 'PENDING' or status == 'RUNNING':
        status = query_action_status(action_id)
        time.sleep(1)
    return status

# DeviceAction
# | ID | MAC | ACTION | FILE | STATUS |#
# Database

host = 'localhost'
user = 'root'
password = '123456'
dbname = 'P2PDevice'

# @in:  action_id
# @out: status
def query_action_status(action_id):
    row = query_action(action_id)
    return row[4] if row else None

# @in:  action_id
# @out: row
def query_action(action_id):
   # return status in ('Pending', 'Running')
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("select * from DeviceAction where ID='%d'" % action_id)
    ret = cursor.fetchone()
    db.close()
    return ret

# @in:  device_id, action, script_name
# @out: action_id
def insert_action(device_id, action, script):
    mac = query_device_mac(device_id)
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("Insert into DeviceAction (ACTION, FILE, STATUS, MAC) "
                   "values('%s', '%s', 'PENDING', '%s')" % (action, script, mac))
    action_id = int(cursor.lastrowid)
    db.commit()
    db.close()
    return action_id

# @in:  action_id, status
# @out: none
def update_action_status(action_id, status):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("Update DeviceAction set STATUS='%s' where ID='%s'" % (status, action_id))
    db.commit()
    db.close()
    pass

def query_device_mac(device_id):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("Select MAC from DeviceInfo where ID='%d'" % (device_id))
    row = cursor.fetchone()
    db.close()
    return row[0]

autoTest()
