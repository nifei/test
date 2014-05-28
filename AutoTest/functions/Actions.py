__author__ = 'test'
import time
import DeviceDB
db = DeviceDB


def run_sync(device_id, script):
    return action_sync(device_id, "EXECUTE", script)

def run_async(device_id, script):
    return action_async(device_id, "EXECUTE", script)

def deploy_sync(device_id, script):
    return action_sync(device_id, "GET", script)

def deploy_async(device_id, script):
    return action_async(device_id, "GET", script)

def action_sync(device_id, action, script):
    action_id = db.insert_action(device_id, action, script)
    status = 'PENDING'
    while status == 'PENDING' or status == 'RUNNING':
        status = db.query_action_status(action_id);
        time.sleep(1)
    return action_id, status

def action_async(device_id, action, script):
    action_id = db.insert_action(device_id, action, script)
    return action_id

def wait(action_id):
    status = db.query_action_status(action_id)
    while status == 'PENDING' or status == 'RUNNING':
        status = db.query_action_status(action_id)
        time.sleep(1)
    return status
