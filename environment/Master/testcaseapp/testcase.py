import jinja2,cgi,os
import unicodedata

# ../bin/gunicorn -w 4 --env HTTP_ACCEPT_LANGUAGE='zh-CN' testcase:app

UploadPath = '/home/test/TestCaseFiles/'

def app(environ, start_response):
    if environ['PATH_INFO']=='/testcase/AutoTest':
        data = AutoTest(environ)
    elif environ['PATH_INFO']=='/testcase/Upload' and environ['REQUEST_METHOD'] == 'POST':
        data = Upload(environ)
    else:
        data = "Hello Gunicorn!\n"
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

def Upload(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)

    try:
        fileitem = form['fileUpLoad']
    except KeyError:
        fileitem = None

    if fileitem != None:
        fn = os.path.basename(fileitem.filename)
        open(UploadPath + fn, 'wb').write(fileitem.file.read())
        message = 'The file "' + fn + '" was uploaded successfully'
    else:
        message = 'No file selected.'

    return message

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

def case_detail_content():
    template = get_template("case_detail_content.html")
    templateVars = {
        "cases" : ["giraffe", "lion", "zebra"]
    }
    return render_template(template, templateVars)

def get_template(file):
    templateLoader = jinja2.FileSystemLoader( searchpath= "/home/test/test/environment/Master/testcaseapp/template/")
    templateEnv = jinja2.Environment(loader = templateLoader, trim_blocks=True, keep_trailing_newline=True)
    template = templateEnv.get_template(file)
    return template

def render_template(template, vars):
    output = template.render(vars)
    return unicodedata.normalize("NFKD", output).encode("utf-8", "ignore")
#print case_detail_content()
