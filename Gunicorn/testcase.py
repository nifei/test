import jinja2,cgi,os
import zipfile,tarfile
import unicodedata
import shutil
import functions.Allocation, functions.Actions
import functions.DeviceDB
import config
import resolve,execute,check

resolve_script_methods = resolve.resolve_script_methods
execute_script_methods = execute.execute_script_methods
check_script_methods = check.check_script_methods
allocation = functions.Allocation
UploadPath = config.UploadPath
TemplatePath = config.TemplatePath
# ../bin/gunicorn -w 4 --env HTTP_ACCEPT_LANGUAGE='zh-CN' testcase:app

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
        prev_task_path = os.path.join(UploadPath, str(prev_task_id))
        if os.path.exists(prev_task_path):
            shutil.rmtree(prev_task_path)
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

