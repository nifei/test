import jinja2,cgi,os
import zipfile,tarfile
import unicodedata
import shutil

# ../bin/gunicorn -w 4 --env HTTP_ACCEPT_LANGUAGE='zh-CN' testcase:app

UploadPath = '/home/test/TestCaseFiles/'

def app(environ, start_response):
    if environ['PATH_INFO']=='/testcase/AutoTest':
        data = AutoTest(environ)
    elif environ['PATH_INFO']=='/testcase/EditCase' and environ['REQUEST_METHOD'] == "GET":
        data = case_detail_content({})
    elif environ['PATH_INFO']=='/testcase/EditCase' and environ['REQUEST_METHOD'] == "POST":
        vars = upload_extract(environ)
        data = case_detail_content(vars)
    else:
        data = environ['PATH_INFO']
        print environ['PATH_INFO']
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
                     "all_cases_content" : all_cases_content(),
                     "case_detail_content" : case_detail_content()
                   }

    return render_template(template, templateVars)

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
    templateLoader = jinja2.FileSystemLoader( searchpath= "/home/test/test/environment/Master/testcaseapp/template/")
    templateEnv = jinja2.Environment(loader = templateLoader, trim_blocks=True, keep_trailing_newline=True)
    template = templateEnv.get_template(file)
    return template

def render_template(template, vars):
    output = template.render(vars)
    return unicodedata.normalize("NFKD", output).encode("utf-8", "ignore")
#print case_detail_content()
