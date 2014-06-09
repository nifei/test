import jinja2,cgi,os
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
            allocation.release_devices(occupied_devices)
            occupied_devices.clear()
            break
        device_list = allocation.find_device(dict, 1)
        if len(device_list) < 1:
            all_found = False
        else:
            shared_count = dict.get('SHARED_COUNT', None)
            all_found, reason = allocation.occupy_device(device_list[0], shared_count)
            if all_found:
                occupied_devices[device_name] = device_list[0]

    for (device_name, device_id) in occupied_devices.items():
        functions.DeviceDB.insert_device_task_relation(task_id, device_id, device_name)
    context={}
    context['occupied_devices'] = occupied_devices
    context['task_id'] = task_id
    context['test_case_name'] = test_case_name
    context['devices_assigned'] = all_found
    data = json.dumps(context)
    return data

def specialize(occupied_devices, test_case_folder):
    shellTemplateLoader = jinja2.FileSystemLoader(searchpath='/')
    shellTemplateEnv = jinja2.Environment(loader = shellTemplateLoader, trim_blocks=True, keep_trailing_newline=True)
    vars = {}
    for (device_name, device_id) in occupied_devices.items():
        device = functions.DeviceDB.query_device(device_id)
        for (key,val) in device.items():
            vars[device_name+'_'+key] = val
    print vars
    for root, folder, subs in os.walk(test_case_folder):
        for file in subs:
            if file.endswith('.sh') and root != test_case_folder:
                script_template = shellTemplateEnv.get_template(os.path.join(root, file))
                print script_template.render(vars)
                with open(os.path.join(root, file), 'w+') as f:
                    f.write(script_template.render(vars))
                    f.close()

def execute_deploy(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    test_case_name = form['test_case_name'].value
    task_id = int(form['task_id'].value)
    return execute_deploy_impl(task_id, test_case_name)

def execute_deploy_impl(task_id, test_case_name):
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    script_module = importlib.import_module('scripts.' + test_case_name)
    deploy_dict = getattr(script_module, 'deploy_dict')
    test_case_path = UploadPath + test_case_name
    specialize(occupied_devices, test_case_path)
    for (device_name, device_id) in occupied_devices.items():
        folder_to_deploy = deploy_dict[device_name]
        subprocess.call("cd %s;tar -cvzf %s.tar.gz %s"%(test_case_path, folder_to_deploy, folder_to_deploy), shell=True)
        tar = deploy_dict[device_name]
        xtar_sh = test_case_name + '/' + 'xtar' + '_' + tar + '.sh'
        with open(UploadPath + '/' + xtar_sh, 'w+') as xtar_sh_file:
            xtar_content = 'mkdir -p %s; tar -xvzf %s -C./%s' % (test_case_name, tar+'.tar.gz', test_case_name)
            xtar_sh_file.write(xtar_content)
        actions.deploy_async(device_id, TestCaseFilesPath + test_case_name + '/' + tar + '.tar.gz', task_id)
        actions.deploy_async(device_id, TestCaseFilesPath +  xtar_sh, task_id)
        actions.run_async(device_id, xtar_sh, task_id)
    data = {}
    data['content'] = json.dumps(occupied_devices, indent=4, separators=(',', ':'))
    data['stop'] = 'false' if len(occupied_devices) > 0 else 'true'
    str = json.dumps(data, indent=4, separators=(',', ':'))
    return str

#execute_deploy_impl(1, 'pair')

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
    'resume': execute_resume
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
    'resume': check_steps
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

