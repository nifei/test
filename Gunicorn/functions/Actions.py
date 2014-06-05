__author__ = 'test'
import time
import DeviceDB
db = DeviceDB

def run_sync(device_id, script, task_id = 0):
    return action_sync(device_id, "EXECUTE", script, task_id)

def run_async(device_id, script, task_id = 0):
    return action_async(device_id, "EXECUTE", script, task_i)

def deploy_sync(device_id, script, task_id = 0):
    return action_sync(device_id, "GET", script, task_id)

def deploy_async(device_id, script, task_id = 0):
    return action_async(device_id, "GET", script, task_id)

def action_sync(device_id, action, script, task_id):
    action_id = db.insert_action(device_id, action, script, task_id)
    status = 'PENDING'
    while status == 'PENDING' or status == 'RUNNING':
        status = db.query_action_status(action_id);
        time.sleep(1)
    return action_id, status

def action_async(device_id, action, script, task_id):
    action_id = db.insert_action(device_id, action, script, task_id)
    return action_id

def wait(action_id):
    status = db.query_action_status(action_id)
    while status == 'PENDING' or status == 'RUNNING':
        status = db.query_action_status(action_id)
        time.sleep(1)
    return status
