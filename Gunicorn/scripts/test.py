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

# TAOWEN
# implement class Task
# usage:
# task = Task(task_id)
# step[i](task)
# function signature:
# def Task.Run(role, script):
#     id = functions.query_task_device_relations [...]
#     functions.Actions.run(id, script)

#def taret_function(Task):
#    Task.Run('server', 'server.sh')

def start_server():
    print "start_server"

def start_client():
    print "start_client"

def end_server():
    print "end_server"

step_list = [ start_server, start_client, end_server ]
