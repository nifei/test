__author__ = 'test'

import functions.DeviceDB
import functions.Actions
import importlib
import sys
import time

def resume(task_id):
    task_info = functions.DeviceDB.query_task(task_id)
    if not task_info:
        return
    test_case_name = task_info['test case']
    script_module = importlib.import_module('scripts.' + test_case_name)
    steps = getattr(script_module, 'step_list')
    functions.DeviceDB.update_task_flag(task_id, 'STOP_FLAG', False)
    functions.DeviceDB.update_task_flag(task_id, 'PAUSE_FLAG', False)
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    broken = False
    current_step = task_info['current step']
    for i in range(current_step+1, len(steps)):
        task_info = functions.DeviceDB.query_task(task_id)
        if task_info['stop flag']:
            functions.DeviceDB.update_task_status(task_id, "NOT RUNNING")
            functions.DeviceDB.update_task_step(task_id, -1)
            broken = True
            break
        if task_info['pause flag']:
            functions.DeviceDB.update_task_status(task_id, "PAUSED")
            broken = True
            break
        functions.DeviceDB.update_task_step(task_id, i)
        steps[i]()
        time.sleep(3)
    if not broken:
        functions.DeviceDB.update_task_step(task_id, -1)
        functions.DeviceDB.update_task_status(task_id, 'FINISHED')

def start(task_id):
    task_info = functions.DeviceDB.query_task(task_id)
    if not task_info:
        return
    test_case_name = task_info['test case']
    script_module = importlib.import_module('scripts.' + test_case_name)
    steps = getattr(script_module, 'step_list')
    functions.DeviceDB.update_task_step(task_id, -1)
    functions.DeviceDB.update_task_status(task_id, 'RUNNING')
    functions.DeviceDB.update_task_flag(task_id, 'STOP_FLAG', False)
    functions.DeviceDB.update_task_flag(task_id, 'PAUSE_FLAG', False)
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    task_action_executor = TaskActionExecutor(task_id, occupied_devices)
    broken = False
    for i in range(len(steps)):
        task_info = functions.DeviceDB.query_task(task_id)
        if task_info['stop flag'] == True:
            functions.DeviceDB.update_task_status(task_id, "NOT RUNNING")
            functions.DeviceDB.update_task_step(task_id, -1)
            broken = True
            break
        if task_info['pause flag'] == True:
            functions.DeviceDB.update_task_status(task_id, "PAUSED")
            broken = True
            break
        functions.DeviceDB.update_task_step(task_id, i)
        steps[i](task_action_executor)
        time.sleep(3)
    if not broken:
        functions.DeviceDB.update_task_step(task_id, -1)
        functions.DeviceDB.update_task_status(task_id, 'FINISHED')

class TaskActionExecutor(object):
    def __init__(self, task_id, occupied_devices):
        self.task_id = task_id
        self.occupied_devices = occupied_devices

    def run_sync(self, device_name, script):
        device_id = self.query_device_id(device_name)
        return functions.Actions.run_sync(device_id, script, self.task_id)

    def run_async(self, device_name, script):
        device_id = self.query_device_id(device_name)
        return functions.Actions.run_async(device_id, script, self.task_id)

    def wait(self, *action_ids):
        for action_id in action_ids:
            functions.Actions.wait(action_id)

    def log(self, msg):
        print(msg)

    def query_device_id(self, device_name):
        return self.occupied_devices[device_name]

operations={
    'start':start,
    'resume':resume
}

if __name__=="__main__":
    if len(sys.argv) != 3:
       print "Task.py start|resume|pause|stop run_id"
       exit (1)
    operation = sys.argv[1]
    task_id = int(sys.argv[2])
    operations[operation](task_id)
