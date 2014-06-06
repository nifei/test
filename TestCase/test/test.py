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

def start_server():
    print "start_server"

def start_client():
    print "start_client"

def end_server():
    print "end_server"

def step_3():
    print "step 3"

def step_4():
    print "step 4"

def step_5():
    print "step 5"

step_list = [ start_server, start_client, end_server, step_3, step_4, step_5 ]
