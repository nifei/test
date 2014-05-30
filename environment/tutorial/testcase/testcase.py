import json

def app(environ, start_response):
    if environ['PATH_INFO']=='/testcase/upload':
        data = upload(environ)
    else:
        data = "Hello, world!\n"
    start_response("200 OK", [
        ("Content-Type", "text/html"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])

def upload(environ):
    print environ
    head = '<html><head><title> Upload </title></head><body><div>'
    tail = '</div></body></html>'
#taowen log lib
    content = "upload:"
    return head+content+tail
