__author__ = 'test'
import time
import MySQLdb

def autoTest():
#    deploy_tar = deploy_async(4, 'download/windows.zip')
#    print "action id:%s, status:%s" % (deploy_tar, wait(deploy_tar))
#    deploy_xtar,status = deploy_sync(4, 'download/xtar-win.sh')
#    print "action id:%s, status:%s" % (deploy_xtar,status)
#    run_xtar,status = run_sync(4, 'download/xtar-win.sh')
#    print "action id:%s, status:%s" % (run_xtar, status)
#    deploy_tar_l = deploy_async(3, 'download/linux.tar.gz')
#    print "action id:%s, status:%s" % (deploy_tar_l, wait(deploy_tar_l))
    deploy_xtar_l,status = deploy_sync(3, 'download/xtar-linux.sh')
    print "action id:%s, status:%s" % (deploy_xtar_l,status)
    run_xtar_l, status = run_sync(3, 'download/xtar-linux.sh')
    print "action id:%s, status:%s" % (run_xtar_l, status)


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
    return row[0] if row else None

autoTest()
