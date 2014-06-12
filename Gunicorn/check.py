__author__ = 'test'
import urlparse
import json
import functions
import functions.Allocation, functions.Actions
import functions.DeviceDB
import config
LogTargetPath = config.LogTargetPath

def check_deploy(environ):
    query_dict = urlparse.parse_qs(environ['QUERY_STRING'])
    token = json.loads(query_dict['token'][0])
    stop = True
    formated_string = 'Role\tIP\tStatus\tFile\n'
    for device_name, action_ids in token.items():
        device_actions = functions.DeviceDB.query_actions_info(action_ids)
        for action in device_actions:
            stop = False if action['STATUS'] in ('PENDING', 'RUNNING') else stop
            formated_string += '%s\t%s\t%s\t%s\n'%(action['ROLE'], action['IP'], action['STATUS'], action['FILE'])

    formated_string = 'Deploying has %sfinished\n\n'%('' if stop else 'not ') + formated_string
    data = {'stop':'true' if stop else 'false', 'content':formated_string, 'token':query_dict['token'][0]}
    return json.dumps(data, indent=4, separators=(',', ':'))

def check_log(environ):
    query_dict = urlparse.parse_qs(environ['QUERY_STRING'])
    task_id = int(query_dict['task_id'][0])
    token = query_dict['token'][0].split(',')
    stop = 'true'
    formatted_string = '\nROLE\tIP\tSTATUS\tFILE\n'
    actions = functions.DeviceDB.query_actions_info(token)
    for action in actions:
        if action['STATUS'] == 'RUNNING' or action['STATUS'] == 'PENDING':
            stop = 'false'
        formatted_string += '%s\t%s\t%s\t%s\n'%(action['ROLE'], action['IP'], action['STATUS'], action['FILE'])
    formatted_string = 'Upload has %sfinished\n'%('' if stop=='true' else 'not ') + formatted_string
    formatted_string = 'Log has uploaded to %s\n'%(LogTargetPath + str(task_id)) if stop=='true' else '' + formatted_string
    return json.dumps({'stop':stop, 'content':formatted_string, 'token':query_dict['token'][0]})

def check_status(environ):
    query_dict = urlparse.parse_qs(environ['QUERY_STRING'])
    task_id = int(query_dict['task_id'][0])
    expected_status = query_dict['expected_result'][0].split(',')
    task_info = functions.DeviceDB.query_task(task_id)
    if task_info:
        if task_info['status'] in expected_status:
            stop = 'true'
            content = 'task is '+ task_info['status']
        else:
            print 'current:' + task_info['status']
            print expected_status
            stop = 'false'
            content = 'waiting...'
    else:
        stop = 'true'
        content = 'task not found'
    return json.dumps({'stop':stop, 'content':content, 'callback':task_info['status']})

def check_steps(environ):
    query_dict = urlparse.parse_qs(environ['QUERY_STRING'])
    task_id = int(query_dict['task_id'][0])
    task_info = functions.DeviceDB.query_task(task_id)
    if task_info:
        current_step = task_info['current step']
        formatted_string = []
        actions_status = functions.DeviceDB.query_task_actions(task_id, 'EXECUTE')
        for action_status in actions_status:
            formatted_string.append('%s\t%s\t%s\t%s'%(action_status['Role'], action_status['IP'], action_status['Status'], action_status['File']))
        formatted_string.append('\nROLE\tIP\tSTATUS\tFILE')
        formatted_string.append('current step:%s'%current_step)
        formatted_string.append('task is %s'%(task_info['status']))
        formatted_string = '\n'.join(reversed(formatted_string))
        stop = 'true' if task_info['status'] != 'RUNNING' else 'false'
    else:
        stop = 'true'
        formatted_string = 'invalid task id'
    return json.dumps({'stop':stop, 'content':formatted_string, 'callback':task_info['status']})

check_script_methods = {
    'deploy': check_deploy,
    'start': check_steps,
    'pause': check_status,
    'stop': check_status,
    'resume': check_steps,
    'log':check_log
}
