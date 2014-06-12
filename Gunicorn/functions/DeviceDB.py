import MySQLdb

__author__ = 'test'
# DeviceAction
# | ID | MAC | ACTION | FILE | STATUS |#
# Database

host = 'localhost'
user = 'root'
password = '123456'
dbname = 'P2PDevice'

# @in: task_id
# @out: dict{device_name:device_id}

def query_device_task_relation(task_id):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("select DEVICE_ID, ROLE from TaskDeviceRelation where TASK_ID=%d"%task_id)
    rows = cursor.fetchall()
    ret = {row[1]:int(row[0]) for row in rows }
    db.close()
    return ret

def clear_device_task_relation(task_id):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("delete from TaskDeviceRelation where TASK_ID=%d"%task_id)
    db.commit()
    db.close()
    return True

# @in: task_id, device_id, role
# @out: relation_id
def insert_device_task_relation(task_id, device_id, device_name):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("insert into TaskDeviceRelation (TASK_ID, DEVICE_ID, ROLE) values(%d, %d, '%s')"%(task_id, device_id, device_name))
    row_id = int(cursor.lastrowid)
    db.commit()
    db.close()
    return row_id

# @in: test_case, task_name,
# @out: task_id

def insert_task(test_case, task_name):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("select ID from Tasks where TASK_NAME='%s' and TEST_CASE='%s'"%(task_name, test_case))
    rows = cursor.fetchall()
    if len(rows) > 0:
        row_id = int(rows[0][0])
    else:
        cursor.execute("insert into Tasks (TASK_NAME, TEST_CASE, CURRENT_STEP, STATUS) values ('%s', '%s', %d, 'NOT RUNNING')"%(task_name, test_case, -1))
        row_id = int(cursor.lastrowid)
        db.commit()
    db.close()
    return row_id

def update_task_flag(task_id, flag_name, flag_value):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("update Tasks set %s=%s where ID=%d"%(flag_name, 'TRUE' if flag_value else 'FALSE',  task_id))
    db.commit()
    db.close()
    return True

def update_task_step(task_id, step):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("update Tasks set CURRENT_STEP=%d where ID=%d"%(step, task_id))
    db.commit()
    db.close()
    return True

def update_task_status(task_id, status):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("update Tasks set STATUS='%s' where ID=%d"%(status, task_id))
    db.commit()
    db.close()
    return True

# @in: task_id
# @out: dict
def query_task(task_id):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    sql = "select TASK_NAME, TEST_CASE, CURRENT_STEP, STOP_FLAG, PAUSE_FLAG, STATUS from Tasks where ID=%d"%task_id
    cursor.execute(sql)
    row = cursor.fetchone()
    db.close()
    return {'task name':row[0], 'test case':row[1], 'current step':int(row[2]), 'stop flag':bool(row[3]), 'pause flag':bool(row[4]), 'status':row[5]} if row and len(row)>0 else None

def query_task_id(test_case_name, task_name):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    sql = "select ID from Tasks where TEST_CASE='%s' and TASK_NAME='%s'"%(test_case_name, task_name)
    cursor.execute(sql)
    row = cursor.fetchone()
    db.close()
    return row[0] if row and len(row)>0 else None

def delete_task(task_id):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    sql = "delete from Tasks where ID=%d"%task_id
    cursor.execute(sql)
    db.commit()
    db.close()
    return True

def delete_task_if_exists(test_case_name, task_name):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    sql = "delete from Tasks where TEST_CASE='%s' and TASK_NAME='%s'"%(test_case_name, task_name)
    cursor.execute(sql)
    affect_rows = db.affected_rows()
    db.commit()
    db.close()
    return True if affect_rows> 0 else False

def delete_task_actions(task_id):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("delete from DeviceAction where TASK_ID=%d"%(task_id))
    db.commit()
    db.close()

# @in: task_id, action_type
def query_task_actions(task_id, action_type):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("select DeviceInfo.ID, TaskDeviceRelation.ROLE, DeviceAction.FILE, DeviceInfo.IP, DeviceAction.STATUS from DeviceAction, DeviceInfo, TaskDeviceRelation where DeviceAction.MAC=DeviceInfo.MAC and TaskDeviceRelation.DEVICE_ID=DeviceInfo.ID and DeviceAction.TASK_ID=%s and TaskDeviceRelation.TASK_ID=%s and DeviceAction.ACTION='%s'"%(task_id, task_id, action_type))
    rows = cursor.fetchall()
    db.close()
    return [{'Device Id':int(row[0])
             , 'Role':row[1]
             , 'File':row[2]
             , 'IP':row[3]
             , 'Status':row[4]
             } for row in rows]

# @in:  action_id
# @out: status
def query_action_status(action_id):
    row = query_action(action_id)
    return row['STATUS'] if row else None

#    if len(device_ids) > 0:
#        id_set = "(%s)" % (",".join("%s" % device_id for device_id in device_ids))
#        db = MySQLdb.connect(host, user, password, dbname)
#        cursor = db.cursor()
#        cursor.execute("Select MAC from DeviceInfo where ID in %s " % (id_set))
#        macs = [item[0] for item in cursor.fetchall()]
#        db.close()
#    else:
#        macs = []
#    return macs
def query_actions(action_ids):
    if len(action_ids) > 0:
        id_set = "(%s)" % (','.join('%s'% action_id for action_id in action_ids))
        db = MySQLdb.connect(host, user, password, dbname)
        cursor = db.cursor()
       #ID	MAC	ACTION	FILE	STATUS	TASK_ID
        cursor.execute("select MAC, ACTION, FILE, STATUS, TASK_ID from DeviceAction where ID in %s" % (id_set))
        actions = [{'MAC':ret[0],
                'ACTION':ret[1],
                'FILE':ret[2],
                'STATUS':ret[3],
                'TASK_ID':ret[4]} for ret in cursor.fetchall()]
        db.close()
        return actions
    else:
        return []

def query_actions_info(action_ids):
    if len(action_ids) > 0:
        id_set = "(%s)" % (','.join('%s'% action_id for action_id in action_ids))
        db = MySQLdb.connect(host, user, password, dbname)
        cursor = db.cursor()
        #ID	MAC	ACTION	FILE	STATUS	TASK_ID
        sql = "select DeviceAction.MAC, " \
              "ACTION, " \
              "FILE, " \
              "DeviceAction.STATUS, " \
              "DeviceAction.TASK_ID, " \
              "DeviceInfo.ID as DeviceID, " \
              "DeviceAction.ID as ActionID," \
              "DeviceInfo.PEERID as PeerID," \
              "DeviceInfo.IP as IP," \
              "TaskDeviceRelation.ROLE as ROLE " \
              "from DeviceAction , DeviceInfo, TaskDeviceRelation where DeviceAction.ID in %s and DeviceAction.MAC=DeviceInfo.MAC and DeviceInfo.ID=TaskDeviceRelation.DEVICE_ID and DeviceAction.TASK_ID=TaskDeviceRelation.TASK_ID" % (id_set)
        cursor.execute(sql)
        actions = [{
                    'MAC':ret[0],
                    'ACTION':ret[1],
                    'FILE':ret[2],
                    'STATUS':ret[3],
                    'TASK_ID':int(ret[4]),
                    'DEVICE_ID':int(ret[5]),
                    'ACTION_ID':int(ret[6]),
                    'PEERID':ret[7],
                    'IP':ret[8],
                    'ROLE':ret[9]
                   } for ret in cursor.fetchall()]
        db.close()
        return actions
    else:
        return []

# @in:  action_id
# @out: row
def query_action(action_id):
   # return status in ('Pending', 'Running')
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
   #ID	MAC	ACTION	FILE	STATUS	TASK_ID
    cursor.execute("select MAC, ACTION, FILE, STATUS, TASK_ID from DeviceAction where ID='%d'" % action_id)
    ret = cursor.fetchone()
    db.close()
    return {'MAC':ret[0],
            'ACTION':ret[1],
            'FILE':ret[2],
            'STATUS':ret[3],
            'TASK_ID':ret[4]}

# @in:  device_id, action, script_name
# @out: action_id
def insert_action(device_id, action, script, task_id):
    mac = query_device_mac(device_id)
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    sql = "Insert into DeviceAction (ACTION, FILE, STATUS, MAC, TASK_ID) \
                   values('%s', '%s', 'PENDING', '%s', '%d')" % (action, script, mac, task_id)
    cursor.execute(sql)
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

def query_device(device_id):
    db = MySQLdb.connect(host, user, password, dbname)
    cursor = db.cursor()
    cursor.execute("Select ID, "
                   "STATUS, "
                   "IP, "
                   "MAC, "
                   "NAT,"
                   "PEERID,"
                   "SHARED_COUNT "
                   "from DeviceInfo where ID= %s " % (device_id))
    row = cursor.fetchone()
    db.close()
    if len(row) > 0:
        device = {
            'ID':int(row[0]),
            'STATUS':row[1],
            'IP':row[2],
            'MAC':row[3],
            'NAT':row[4],
            'PEERID':row[5],
            'SHARED_COUNT':row[6]
        }
    else:
        device = None
    return device
#ID	STATUS	IP	MAC	NETTYPE	NAT	TUNNEL	PEERID	SHARED_COUNT

# @in: device_ids = [1,2,3...]
def query_device_macs(device_ids):
    if len(device_ids) > 0:
        id_set = "(%s)" % (",".join("%s" % device_id for device_id in device_ids))
        db = MySQLdb.connect(host, user, password, dbname)
        cursor = db.cursor()
        cursor.execute("Select MAC from DeviceInfo where ID in %s " % (id_set))
        macs = [item[0] for item in cursor.fetchall()]
        db.close()
    else:
        macs = []
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

