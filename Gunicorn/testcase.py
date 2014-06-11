import jinja2,cgi,os,stat,string
import zipfile,tarfile
import unicodedata
import shutil
import importlib
import json
import inspect
import functions.Allocation, functions.Actions
import functions.DeviceDB
import urlparse
import subprocess
import config

actions = functions.Actions
allocation = functions.Allocation
UploadPath = config.UploadPath
TestCaseFilesPath = config.TestCaseFilesPath
TemplatePath = config.TemplatePath
ScriptPath = config.ScriptPath
LogPath = '/home/test/Agent/Log/'
LogTargetPath = 'Log/'
HostString = 'test@192.168.91.123'
# ../bin/gunicorn -w 4 --env HTTP_ACCEPT_LANGUAGE='zh-CN' testcase:app

def resolve_query_dict(test_case_name):
    script_module = importlib.import_module('scripts.' + test_case_name)
    test_attr = getattr(script_module, 'query_dict')
    return "resolve query:" + test_case_name + '\n' + "query_dict = " + json.dumps(test_attr, indent=4, separators=(',', ':'))

def resolve_deploy_dict(test_case_name):
    script_module = importlib.import_module('scripts.' + test_case_name)
    test_attr = getattr(script_module, 'deploy_dict')
    return "resolve deploy:" + test_case_name + '\n' + "deploy_dict = " + json.dumps(test_attr, indent=4, separators=(',', ':'))

def resolve_step_list(test_case_name):
    script_module = importlib.import_module('scripts.' + test_case_name)
    try:
        test_attr = getattr(script_module, 'step_list')
        class FuncEncoder(json.JSONEncoder):
            def default(self, func):
                return [line.rstrip('\n').replace('\"', ' ') for line in inspect.getsourcelines(func)[0]]
        data = "resolve steps:" + test_case_name + '\n' + "step_list = " + json.dumps(test_attr, cls=FuncEncoder, indent=4, separators=(',', ':'))
    except:
        data = "No steps found, please assign steps to run like this:\n" \
               "def run_server(): \n" \
               "    run_sync(server_id, 'server.sh') \n" \
               "def run_client(): \n" \
               "    run_sync(client_id, 'client.sh') \n" \
               "step_list = [ run_server, run_client ] \n"
    return data

resolve_script_methods = {
    'query': resolve_query_dict,
    'deploy': resolve_deploy_dict,
    'steps': resolve_step_list
    }

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

def execute_deploy(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    test_case_name = form['test_case_name'].value
    task_id = int(form['task_id'].value)
    return execute_deploy_impl(task_id, test_case_name)

def write_upload_log_bash(bash_file, log_path, host_string, target_path):
    with open(bash_file, 'w+') as f:
        content = "pscp -r -pw '123456' -P 8022 %s* %s:%s"%(log_path, host_string, target_path)
        f.write(content)
        f.close()
        os.chmod(bash_file, os.stat(bash_file).st_mode | stat.S_IEXEC)

def execute_deploy_impl(task_id, test_case_name):
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    script_module = importlib.import_module('scripts.' + test_case_name)
    deploy_dict = getattr(script_module, 'deploy_dict')
    str_task_id = '%d'%task_id
    task_path = UploadPath + str_task_id
    subprocess.call('mkdir -p %s'%(task_path), shell=True)
    copycmd = 'cp %s %s -r;'%(UploadPath + test_case_name + '/*', task_path + '/')
    subprocess.call(copycmd, shell=True)
    specialize(occupied_devices, task_path, task_id)
    for (device_name, device_id) in occupied_devices.items():
        folder_to_deploy = deploy_dict[device_name]
        log_upload_sh = task_path + '/' + folder_to_deploy + '/' + 'upload_log.sh'
        log_path_agent = LogPath + str_task_id + '/'
        log_upload_target = LogTargetPath + str_task_id + '/' + device_name
        make_log_folder = 'mkdir -p %s'%log_upload_target
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
        actions.deploy_async(device_id, TestCaseFilesPath + str_task_id + '/' + tar + '.tar.gz', task_id)
        actions.deploy_async(device_id, TestCaseFilesPath + str_task_id + '/' + xtar_sh, task_id)
        actions.run_async(device_id, xtar_sh, task_id)
    data = {}
    data['content'] = json.dumps(occupied_devices, indent=4, separators=(',', ':'))
    data['stop'] = 'false' if len(occupied_devices) > 0 else 'true'
    str = json.dumps(data, indent=4, separators=(',', ':'))
    return str

#execute_deploy_impl(88, 'pair')

def execute_start(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    subprocess.call("python ./Tasks.py start %s &"%task_id, shell=True)
    return json.dumps({"stop":"false", "content":"Test task starts. "})

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
    return json.dumps({"stop":"false", "content":"HIAHIAHIA"})

def execute_release(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    if not task_id or task_id <= 0 or task_id == None:
        return "invalid task id"
    allocation.release_task_devices(task_id)
    return "released"

execute_script_methods = {
    'query': execute_query,
    'release': execute_release,
    'deploy': execute_deploy,
    'start': execute_start,
    'stop': execute_stop,
    'pause': execute_pause,
    'resume': execute_resume,
    'log': execute_log
}

def check_deploy(environ):
    query_dict = urlparse.parse_qs(environ['QUERY_STRING'])
    task_id = int(query_dict['task_id'][0])
    actions_status = functions.DeviceDB.query_task_actions(task_id, 'GET')
    formated_string = 'Device Id\tRole\tFile\tIP\tStatus\n'
    stop = 'true'
    for action_status in actions_status:
        formated_string += '%d\t%s\t%s\t%s\t%s\n'%(action_status['Device Id'], action_status['Role'], action_status['File'], action_status['IP'], action_status['Status'])
        if action_status['Status'] in ('PENDING','RUNNING'):
            stop = 'false'
    data = {'stop':stop, 'content':formated_string}
    return json.dumps(data, indent=4, separators=(',', ':'))

def check_log(environ):
    query_dict = urlparse.parse_qs(environ['QUERY_STRING'])
    task_id = int(query_dict['task_id'][0])
    formatted_string = '(*_*)~'
    return json.dumps({'stop':'true', 'content':formatted_string})

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
        if task_info['status'] != 'RUNNING':
            formatted_string = 'task is ' + task_info['status'] + '\n'
            stop = 'true'
        else:
            formatted_string = 'current step:%s\n'%current_step
            actions_status = functions.DeviceDB.query_task_actions(task_id, 'EXECUTE')
            formatted_string += 'Device Id\tRole\tFile\tIP\tStatus\n'
            for action_status in actions_status:
                formatted_string += '%d\t%s\t%s\t%s\t%s\n'%(action_status['Device Id'], action_status['Role'], action_status['File'], action_status['IP'], action_status['Status'])
            stop = 'false'
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

def app(environ, start_response):
    if environ['PATH_INFO']=='/testcase/AutoTest':
        data = AutoTest(environ)
    elif environ['PATH_INFO']=='/testcase/EditCase' and environ['REQUEST_METHOD'] == "GET":
        data = case_detail_content({})
    elif environ['PATH_INFO']=='/testcase/EditCase' and environ['REQUEST_METHOD'] == "POST":
        vars = upload_extract(environ)
        data = case_detail_content(vars)
    elif environ['PATH_INFO']=='/testcase/scripts/newtask' and environ['REQUEST_METHOD'] == "POST":
        data = new_task(environ)
    elif environ['PATH_INFO'].startswith('/testcase/scripts/resolve/'):
        form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
        test_case_name = form['test_case_name'].value
        target = os.path.basename(environ['PATH_INFO'])
        data = resolve_script_methods[target](test_case_name)
    elif environ['PATH_INFO'].startswith('/testcase/scripts/execute/') and environ['REQUEST_METHOD'] == "POST":
        target = os.path.basename(environ['PATH_INFO'])
        data = execute_script_methods[target](environ)
    elif environ['PATH_INFO'].startswith('/testcase/scripts/check/') and environ['REQUEST_METHOD'] == "GET":
        target = os.path.basename(environ['PATH_INFO'])
        data = check_script_methods[target](environ)
    else:
        data = environ['PATH_INFO']
        print data
    start_response("200 OK", [
        ("Content-Type", "text/html;charset=utf8"),
        ("Content-Length", str(len(data))),
        ("Accept-Charset", "utf-8")
    ])
    return iter([data])

def AutoTest(environ):
    template = get_template( "AutoTest.html" )

    templateVars = {
                     "running_cases_content" : running_cases_content(),
                     "all_cases_content" : all_cases_content()
                   }

    return render_template(template, templateVars)

def new_task(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    test_case_name = form['test_case_name'].value
    task_name = form['task_name'].value
    return new_task_impl(test_case_name, task_name)

def new_task_impl(test_case_name, task_name):
    prev_task_id = functions.DeviceDB.query_task_id(test_case_name, task_name)
    if prev_task_id and prev_task_id > 0:
        allocation.release_task_devices(prev_task_id)
        functions.DeviceDB.delete_task_actions(prev_task_id)
        functions.DeviceDB.delete_task(prev_task_id)
    task_id = functions.DeviceDB.insert_task(test_case_name, task_name)
    return str(task_id)

def upload_extract(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    fileitem = form['fileUpLoad']
    if fileitem != None:
        file_name = os.path.basename(fileitem.filename)
        local_file = UploadPath + file_name
        open(local_file, 'wb').write(fileitem.file.read())
        test_case_name = file_name.split('.')[0]
        local_folder = UploadPath + test_case_name + '/'
        ext = file_name.split('.')[-1]
        if ext == 'zip':
            zipfile.ZipFile(local_file).extractall(local_folder)
        elif ext == 'tar':
            tarfile.open(local_file, 'r').extractall(local_folder)
        else:
            tarfile.open(local_file, 'r:gz').extractall(local_folder)

        def end_filter(*endstring):
            ends = endstring
            def run(s):
                f = map(s.endswith, ends)
                if True in f: return s
            return run

        pys = filter(end_filter('.py'), os.listdir(local_folder))
        folders = [ d for d in os.listdir(local_folder) 
		if os.path.isdir(local_folder+'/'+d)] 
        if len(pys) > 0 and pys[0] == test_case_name+'.py':
            script_file = pys[0]
            shutil.copyfile(local_folder + script_file, './scripts/' + script_file)
        else:
            script_file = 'Not Found'
        return {
            'test_case_name': test_case_name,
            'script_file': script_file,
            'tars': folders
            }
    else:
        return {'test_case_name': 'Invalid File' }

def running_cases_content():
    template = get_template("running_cases_content.html")
    templateVars = {
        "cases" : ["giraffe", "lion", "zebra"]
    }
    return render_template(template, templateVars)

def all_cases_content():
    template = get_template("all_cases_content.html")
    templateVars = {
        "cases" : ["giraffe", "lion", "zebra"]
    }
    return render_template(template, templateVars)

def case_detail_content(vars):
    template = get_template("case_detail_content.html")
    return render_template(template, vars)

def get_template(file):
    templateLoader = jinja2.FileSystemLoader( searchpath= TemplatePath)
    templateEnv = jinja2.Environment(loader = templateLoader, trim_blocks=True, keep_trailing_newline=True)
    template = templateEnv.get_template(file)
    return template

def render_template(template, vars):
    output = template.render(vars)
    return unicodedata.normalize("NFKD", output).encode("utf-8", "ignore")

