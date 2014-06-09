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
    'server': query_none
}

deploy_dict = {
    'server': 'server.tar.gz'
}

def start_server(i):
    i.log('start_server')
    i.run_sync('server', 'single/server/start.sh')

#def start_client(i):
#    i.log('start_client')
#    i.wait(
#        i.run_async('client1', 'start'),
#        i.run_async('client2', 'start')
#    )
#
#def end_server(i):
#    i.log('end_server')
#    i.run_sync('server', 'end')

step_list = [ start_server ] #, start_client, end_server ]
