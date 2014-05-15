#!/usr/bin/env python

import os
import pickle

def run_id_to_topo(run_id):
    file_name = './%s.pkl' % run_id 
    if os.path.isfile(file_name):
        topo_file = open(file_name,'rb')
        topo = pickle.load(topo_file)
        topo_file.close()
    else:
        topo = {'hosts':{},'connections':{},'network_loads':{},'cpu_loads':{},'runId':run_id,'protocol':''}

    return topo

def topo_to_run_id_pkl(topo, run_id):
    topo_file = open('./%s.pkl' % run_id , 'wb')
    pickle.dump(topo, topo_file)
    topo_file.close()

def add_host_to_topo(ip, login_ip,login_port, shell, host_id, topo):
    topo['hosts'][host_id]={'ip':ip,'login_ip':login_ip,'login_port':login_port,'shell':shell,'id':host_id}
    return topo

def add_host(ip, login_ip, login_port, shell, host_id, run_id):
    topo = load_topo(run_id)
    topo = add_host_to_topo(ip, login_ip,login_port, shell, host_id, topo)  
    save_topo(topo, run_id)

def add_connection_to_topo(id_s, id_c, port, data_size, protocol, connection_id, topo):
    topo['connections'][connection_id]= {'server':id_s, 'client':id_c, 'port':port, 'bytes':data_size,'protocol':protocol, 'type':'Test'}
    return topo
 
def add_connection(id_s, id_c, port, data_size,protocol, connection_id,run_id):
    topo = load_topo(run_id) 
    topo = add_connection_to_topo(id_s, id_c, port, data_size,protocol, connection_id,topo)
    save_topo(topo,run_id)

def add_load_connection_to_topo(id_s, id_c, port, data_per_thread, connection_id, thread_count, protocol, topo):
    topo['connections'][connection_id] = {'server':id_s, 'client':id_c, 'port':port, 'bytes':data_per_thread, 'type':'Network Load', 'thread-count':thread_count, 'protocol':protocol}
    return topo

def add_load_connection(id_s, id_c, port, data_per_thread,connection_id, thread_count, protocol, run_id):
    topo = load_topo(run_id)
    topo = add_load_connection_to_topo(id_s, id_c, port, data_per_thread, connection_id,thread_count, protocol, topo)
    save_topo(topo,run_id)

def add_parallel_connection(seq, connection_id, run_id):
    topo = load_topo(run_id)
    topo = add_parallel_connection_to_topo(seq, connection_id, topo)
    save_topo(topo, run_id)

def add_parallel_connection_to_topo(seq, connection_id,topo):
    topo.setdefault('seqs',{})
    topo['seqs'].setdefault(seq,{'connections':[],'stressed_hosts':[]})
    topo['seqs'][seq]['connections'].append(connection_id)
    return topo

def add_parallel_cpu_stress(seq, host_id, stress_time,run_id):
    topo = load_topo(run_id)
    topo = add_parallel_cpu_stress_to_topo(seq, host_id, stress_time,topo)
    save_topo(topo, run_id)

def add_parallel_cpu_stress_to_topo(seq, host_id, stress_time, topo):
    topo.setdefault('seqs',{})
    topo['seqs'].setdefault(seq,{'connections':[],'stressed_hosts':[]})
    topo['seqs'][seq]['stressed_hosts'].append((host_id,stress_time))
    return topo

def set_protocol(protocol,run_id):
    topo = load_topo(run_id)
    topo['protocol'] = protocol
    save_topo(topo,run_id)
    return topo


