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
import threading
actions = functions.Actions
allocation = functions.Allocation

# ../bin/gunicorn -w 4 --env HTTP_ACCEPT_LANGUAGE='zh-CN' testcase:app

UploadPath = '/home/test/TestCaseFiles/'

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

def execute_deploy(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    test_case_name = form['test_case_name'].value
    task_id = int(form['task_id'].value)

    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    script_module = importlib.import_module('scripts.' + test_case_name)
    deploy_dict = getattr(script_module, 'deploy_dict')
    data = {}
    for (device_name, device_id) in occupied_devices.items():
        tar = deploy_dict[device_name]
        xtar_sh = UploadPath + test_case_name + '/' + 'xtar' + '_' + tar + '.sh'
        with open(xtar_sh, 'w+') as xtar_sh_file:
            xtar_sh_file.write('tar -xvzf %s ./%s' % (tar, test_case_name))
        actions.deploy_async(device_id, test_case_name + '/' + tar, task_id)
    data['content'] = json.dumps(occupied_devices, indent=4, separators=(',', ':'))
    data['stop'] = 'false' if len(occupied_devices) > 0 else 'true'
    return json.dumps(data, indent=4, separators=(',', ':'))

def execute_steps(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    task_id = int(form['task_id'].value)
    return execute_task(task_id)

def execute_task(task_id):
    task_info = functions.DeviceDB.query_task(task_id)
    task_name = task_info['task name']
    test_case_name = task_info['test case']
    script_module = importlib.import_module('scripts.' + test_case_name)
    step_list = getattr(script_module, 'step_list')
    lock=threading.Lock()
    threading.Thread(target=run_task, args=(task_id, step_list), name='thread-'+test_case_name+task_name)
    return "Success"

def run_task(task_id, steps):
    occupied_devices = functions.DeviceDB.query_device_task_relation(task_id)
    for step in steps:
        step()

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
    'steps': execute_steps
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
    return json.dumps({'stop':stop, 'content':formated_string}, indent=4, separators=(',', ':'))

check_script_methods = {
    'deploy': check_deploy
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
        tars = filter(end_filter('.tar.gz', '.tar', '.zip'), os.listdir(local_folder))
        if pys[0]:
            script_file = pys[0]
            shutil.copyfile(local_folder + script_file, './scripts/' + script_file)
        else:
            script_file = 'Not Found'
        return {
            'test_case_name': test_case_name,
            'script_file': script_file,
            'tars': tars
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
    templateLoader = jinja2.FileSystemLoader( searchpath= "/home/test/test/Gunicorn/template/")
    templateEnv = jinja2.Environment(loader = templateLoader, trim_blocks=True, keep_trailing_newline=True)
    template = templateEnv.get_template(file)
    return template

def render_template(template, vars):
    output = template.render(vars)
    return unicodedata.normalize("NFKD", output).encode("utf-8", "ignore")

#data, devices = execute_query('test')
#print data
#allocation.release_devices(devices.values())
