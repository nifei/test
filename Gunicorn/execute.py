__author__ = 'test'
import importlib
import json
import jinja2
import cgi
import os
import functions
import stat
import subprocess
import functions.Allocation, functions.Actions
import functions.DeviceDB
import config
import shutil
import functions.Files

actions = functions.Actions
allocation = functions.Allocation
UploadPath = config.UploadPath
TestCaseFilesPath = config.TestCaseFilesPath
LogPath = config.LogPath
HostString = config.HostString
LogTargetPath = config.LogTargetPath
LogMasterPath = config.LogMasterPath
listFiles = functions.Files.listFiles
SCPLogin = config.SCPLogin

def execute_query(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    test_case_name = form['test_case_name'].value
    task_id = int(form['task_id'].value)
    if not task_id or task_id <= 0 or task_id == None:
        return "invalid task id"
   # Clear previous occupied devices
    allocation.release_task_devices(task_id)
    script_module = importlib.import_module('scripts.' + test_case_name)

    query_dict = getattr(script_module, 'query_dict')
    all_found = True
    occupied_devices = {}
    for (device_name, dict) in query_dict.items():
        if all_found == False:
            break

        device_list = allocation.find_device(dict, 1)
        if len(device_list) < 1:
            all_found = False
        else:
            shared_count = dict.get('SHARED_COUNT', None)
            all_found, reason = allocation.occupy_device(device_list[0], shared_count)
            if all_found:
                occupied_devices[device_name] = device_list[0]

    if not all_found:
        allocation.release_devices(occupied_devices)
        occupied_devices.clear()
    else:
        for (device_name, device_id) in occupied_devices.items():
            functions.DeviceDB.insert_device_task_relation(task_id, device_id, device_name)
    data = 'devices found:' + str(all_found) + '\n'
    data += 'devices name-id:\n'
    data += json.dumps(occupied_devices, indent=4, separators=(',', ':'))
    return data


def execute_deploy(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    test_case_name = form['test_case_name'].value
    task_id = int(form['task_id'].value)
    return execute_deploy_impl(task_id, test_case_name)

def write_upload_log_bash(bash_file, log_path, host_string, target_path):
    with open(bash_file, 'w+') as f:
        content = SCPLogin%(log_path, host_string, target_path)
        f.write(content)
        f.close()
        os.chmod(bash_file, os.stat(bash_file).st_mode | stat.S_IEXEC)

def specialize(occupied_devices, test_case_folder, task_id):
    shellTemplateLoader = jinja2.FileSystemLoader(searchpath='/')
    shellTemplateEnv = jinja2.Environment(loader = shellTemplateLoader, trim_blocks=True, keep_trailing_newline=True)
    vars = {}
    vars['log_dir'] = '%s%d/'%(LogPath,task_id)
    for (device_name, device_id) in occupied_devices.items():
        device = functions.DeviceDB.query_device(device_id)
        for (key,val) in device.items():
            vars[device_name+'_'+key] = val
    for root, folder, subs in os.walk(test_case_folder):
        for file in subs:
            if file.endswith('.sh') and root != test_case_folder:
                script_template = shellTemplateEnv.get_template(os.path.join(root, file))
                with open(os.path.join(root, file), 'w+') as f:
                    c = script_template.render(vars)
                    f.write(c)
                    f.close()

def make_task_folder(task_id, test_case_name):
    task_path = UploadPath + str(task_id)
    if os.path.exists(task_path):
        shutil.rmtree(task_path)
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    shutil.copytree(os.path.join(UploadPath, test_case_name), task_path)
    specialize(occupied_devices, task_path, task_id)

def execute_deploy_impl(task_id, test_case_name):
    make_task_folder(task_id, test_case_name)
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    script_module = importlib.import_module('scripts.' + test_case_name)
    deploy_dict = getattr(script_module, 'deploy_dict')
    task_path = UploadPath + '%d'%task_id

    token = {}
    for (device_name, device_id) in occupied_devices.items():
        folder_to_deploy = deploy_dict[device_name]
        log_upload_sh = task_path + '/' + folder_to_deploy + '/' + 'upload_log.sh'
        log_path_agent = LogPath + '%d'%task_id + '/'
        log_upload_target = LogTargetPath + '%d'%task_id + '/' + device_name
        make_log_folder = 'mkdir -p ~/%s'%log_upload_target
        subprocess.call(make_log_folder, shell = True)
        write_upload_log_bash(log_upload_sh, log_path_agent, HostString, log_upload_target)

        tarcmd ='cd %s; tar -czf %s.tar.gz %s'%(task_path, folder_to_deploy, folder_to_deploy)
        subprocess.call(tarcmd, shell=True)
        tar = deploy_dict[device_name]
        xtar_sh = 'xtar' + '_' + tar + '.sh'
        xtar_sh_path = task_path + '/' + xtar_sh
        with open(xtar_sh_path, 'w+') as xtar_sh_file:
            xtar_content = 'mkdir -p %s; tar -xvzf %s -C ./%s;mkdir -p %s' % (test_case_name, tar+'.tar.gz', test_case_name, log_path_agent)
            xtar_sh_file.write(xtar_content)
            xtar_sh_file.close()
            os.chmod(xtar_sh_path, os.stat(xtar_sh_path).st_mode | stat.S_IEXEC)
        token[device_name] = []
        token[device_name].append(actions.deploy_async(device_id, TestCaseFilesPath + '%d'%task_id + '/' + tar + '.tar.gz', task_id))
        token[device_name].append(actions.deploy_async(device_id, TestCaseFilesPath + '%d'%task_id + '/' + xtar_sh, task_id))
        token[device_name].append(actions.run_async(device_id, xtar_sh, task_id))
    data = {}
    data['content'] = json.dumps(occupied_devices, indent=4, separators=(',', ':'))
    data['stop'] = 'false' if len(occupied_devices) > 0 else 'true'
    data['token'] = json.dumps(token)
    str = json.dumps(data, indent=4, separators=(',', ':'))
    return str

def execute_start(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    subprocess.call("python ./Tasks.py start %s &"%task_id, shell=True)
    return json.dumps({"stop":"false", "content":"Test task starts. ", 'token':task_id})

def execute_stop(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    task_info = functions.DeviceDB.query_task(task_id)
    if task_info['status'] != 'RUNNING':
        functions.DeviceDB.update_task_status(task_id, 'NOT RUNNING')
        stop = 'true'
        content = 'task is NOT RUNNING'
    else:
        functions.DeviceDB.update_task_flag(task_id, 'STOP_FLAG', True)
        stop = 'false'
        content = 'stopping...'
    return json.dumps({'stop':stop, 'content': content})

def execute_pause(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    functions.DeviceDB.update_task_flag(task_id, 'PAUSE_FLAG', True)
    return json.dumps({'stop':'false', 'content': 'pausing...'})

def execute_resume(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    subprocess.call("python ./Tasks.py resume %s &"%task_id, shell=True)
    return json.dumps({"stop":"false", "content":"Test task continued. "})

def execute_log(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    test_case_name = form['test_case_name'].value
    script_module = importlib.import_module('scripts.' + test_case_name)
    deploy_dict = getattr(script_module, 'deploy_dict')
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    token=[]
    for (device_name, device_id) in occupied_devices.items():
        upload_log_path = test_case_name + '/' + deploy_dict[device_name] + '/' +  'upload_log.sh'
        token.append(actions.run_async(device_id, upload_log_path, task_id))
    return json.dumps({"stop":"false", "content":"HIAHIAHIA", "token":token})

def execute_release(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    if not task_id or task_id <= 0 or task_id == None:
        return "invalid task id"
    allocation.release_task_devices(task_id)
    return "released"

def execute_viewlog(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    format_string=list(listFiles(LogMasterPath+str(task_id), None))
    return ''.join(format_string)

def execute_shell(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    test_case_name = form['test_case_name'].value
    make_task_folder(task_id, test_case_name)
    format_string=[]
    format_string += listFiles(os.path.join(UploadPath, str(task_id)),'sh')
    return ''.join(format_string)

execute_script_methods = {
    'query': execute_query,
    'release': execute_release,
    'deploy': execute_deploy,
    'shells': execute_shell,
    'start': execute_start,
    'stop': execute_stop,
    'pause': execute_pause,
    'resume': execute_resume,
    'log': execute_log,
    'viewlog': execute_viewlog
}
