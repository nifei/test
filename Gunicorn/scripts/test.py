__author__='test'

SHARED_OCCUPIED=(-1, None)
TOTALLY_FREE=0

query_none = {
    "NAT": ["None", "Cone"],
    "NATTYPE": "yidong",
    "SHARED_COUNT": SHARED_OCCUPIED,
    "STATUS": "Online"
}
query_cone = {
    "NAT": "Cone",
    "SHARED_COUNT": TOTALLY_FREE,
    "STATUS": "Online"
}

query_dict = {
    'server': query_none,
    'client1': query_cone,
    'client2': query_cone
}

deploy_dict = {
    'server': 'dev1.tar.gz',
    'client1': 'dev2.tar.gz',
    'client2': 'dev2.tar.gz'
}

def start_server(i):
    i.run_sync('server', 'start')
    print "start_server"

def start_client(i):
    i.wait(
        i.run_async('client1', 'start'),
        i.run_async('client2', 'start'))
    print "start_client"

def end_server(i):
    i.run_sync('server', 'end')
    print "end_server"

step_list = [ start_server, start_client, end_server ]
