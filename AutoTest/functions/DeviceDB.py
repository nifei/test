import MySQLdb

__author__ = 'test'
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

# @in: device_ids = [1,2,3...]
def query_device_macs(device_ids):
    id_set = "(%s)" % (",".join("%s" % device_id for device_id in device_ids))
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("Select MAC from DeviceInfo where ID in %s " % (id_set))
    macs = [item[0] for item in cursor.fetchall()]
    db.close()
    return macs

def query_device_ids_by_filter(where_filter, count):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    if count:
        cmd = "select * from DeviceInfo %s limit %d" % (where_filter, count)
    else:
        cmd = "select * from DeviceInfo %s " % (where_filter)
    cursor.execute(cmd)
    rows = cursor.fetchall()
    db.close()
    return [int(item[0]) for item in rows]

def increase_shared_device(device_macs):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    # check shared status of devices
    mac_set = "(%s)"%(','.join("'%s'" % device_mac for device_mac in device_macs))
    cursor.execute("select SHARED_COUNT from DeviceInfo where MAC in %s"%mac_set)
    statuses = [status[0] for status in cursor.fetchall()]
    if -1 in statuses:
        ret, reason = False, "Some device is exclusively occupied"
    else:
        cursor.execute("update DeviceInfo set SHARED_COUNT=SHARED_COUNT+1 where MAC in %s"%mac_set)
        db.commit()
        ret, reason = True, None
    db.close()
    return ret, reason

def lock_exclusive_device(device_macs):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    mac_set = "(%s)"%(','.join("'%s'" % device_mac for device_mac in device_macs))
    cursor.execute("select SHARED_COUNT from DeviceInfo where MAC in %s"%mac_set)
    statuses = [status[0] for status in cursor.fetchall()]
    if len(filter(lambda x: x!=0, statuses))>0:
        ret, reason = False, "Some device is occupied"
    else:
        cursor.execute("update DeviceInfo set SHARED_COUNT=-1 where MAC in %s"%mac_set)
        db.commit()
        ret, reason = True, None
    db.close()
    return ret, reason

def release_device(device_macs):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    for mac in device_macs:
        cursor.execute("select SHARED_COUNT from DeviceInfo where MAC='%s'"%mac)
        shared_count = cursor.fetchone()[0]
        if shared_count == -1: # exclusive
            command = "update DeviceInfo set SHARED_COUNT=0 where MAC='%s'"%mac
        elif shared_count > 0: # shared
            command = "update DeviceInfo set SHARED_COUNT=SHARED_COUNT-1 where MAC='%s'"%mac
        else:
            command = None
        if command:
            cursor.execute(command)
    db.commit()
