import json

def app(environ, start_response):
    if environ['PATH_INFO']=='/testcase/AutoTest.html':
        data = AutoTest(environ)
    else:
        data = "Hello, world!\n"
    start_response("200 OK", [
        ("Content-Type", "text/html"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])

def AutoTest(environ):
    print environ
    head = '<html><head><title> Upload </title></head><body><div>'
    tail = '</div></body></html>'
#taowen log lib
    content = "Auto Test Page:"
    return head+content+tail
