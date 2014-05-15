#!/usr/bin/env pyth/n

from __future__ import with_statement
from fabric.api import local, settings, abort, run, cd, sudo, env, roles, hide
from fabric.contrib.console import confirm
from fabric.tasks import execute
import pys.sync, pys.topo, pys.dump
import os,time, subprocess, re,csv
import testdata

deploy = pys.sync.deploy
deploy_binary = pys.sync.deploy_binary
save_topo = pys.topo.topo_to_run_id_pkl
load_topo = pys.topo.run_id_to_topo

env.password='123456'
env.user='test'

env.warnOnly=False

#env.linux_shell='/bin/bash -l -c'
#env.windows_shell='cmd.exe /c c:/msys/1.0/bin/sh.exe -l -c'

def test_host(login_ip, login_port, shell):
    with settings(host_string='test@%s:%s'%(login_ip,login_port), shell = shell):
        run('pwd')
        run('ls')
        sid = run('./StartIperf.sh -s TCP',pty=False)
        cid = run('./StartIperf.sh -c TCP 127.0.0.1',pty=False)
        run('ps -ef|grep perf')
        run('kill %s'%sid)
        run('kill %s'%cid)

def use_default_topo(run_id):
    testdata.default_topo['runId']=run_id
    save_topo(testdata.default_topo, run_id)

def set_host(hid, ip, login_ip, login_port, shell, run_id):
    topo = load_topo(run_id)
    topo['hosts'].setdefault(hid,{})
    topo['hosts'][hid]={
        'ip':ip,
        'login_ip':login_ip,
        'login_port':login_port,
        'shell':shell,
        'id':hid
    }
    save_topo(topo, run_id)

def run_all_connections(run_id):
    topo = load_topo(run_id)
    run_all_connections_in_topo(topo)

def run_all_connections_in_topo(topo):
    for (seq_id, step) in sorted(topo['seqs'].items()):
        print('===================Step %s=========================='%seq_id)
        run_step(step, topo)
        time.sleep(3)

def before_run_test(run_id):
    topo = load_topo(run_id)
    local('rm ./tmp/%s.* -f'%run_id)
    local('mkdir tmp -p')
    rules_dict = {}
    for (key,connection) in topo['connections'].items():
        if connection['type'] == 'Test':
            server = topo['hosts'][connection['server']]
            client = topo['hosts'][connection['client']]
            rule_so= 'iptables -A OUTPUT -s %s -d %s -p tcp --sport %s -j P2P'%(server['ip'],client['ip'],connection['port'])
            rule_so_udp= 'iptables -A OUTPUT -s %s -d %s -p udp --sport %s -j P2P'%(server['ip'],client['ip'],connection['port'])
            rule_si = 'iptables -A INPUT -s %s -d %s -p tcp --dport %s -j P2P'%(client['ip'],server['ip'],connection['port'])
            rule_si_udp = 'iptables -A INPUT -s %s -d %s -p udp --dport %s -j P2P'%(client['ip'],server['ip'],connection['port'])
            rules_dict.setdefault(connection['server'],[]).append(rule_so)
            rules_dict[connection['server']].append(rule_si)
            rules_dict[connection['server']].append(rule_si_udp)
            rules_dict[connection['server']].append(rule_so_udp)

            rule_co = 'iptables -A OUTPUT -s %s -d %s -p tcp --dport %s -j P2P'%(client['ip'],server['ip'],connection['port'])
            rule_ci = 'iptables -A INPUT -s %s -d %s -p tcp --sport %s -j P2P'%(server['ip'],client['ip'],connection['port'])
            rule_co_udp = 'iptables -A OUTPUT -s %s -d %s -p udp --dport %s -j P2P'%(client['ip'],server['ip'],connection['port'])
            rule_ci_udp = 'iptables -A INPUT -s %s -d %s -p udp --sport %s -j P2P'%(server['ip'],client['ip'],connection['port'])
            rules_dict.setdefault(connection['client'],[]).append(rule_co)
            rules_dict[connection['client']].append(rule_ci)
            rules_dict[connection['client']].append(rule_ci_udp)
            rules_dict[connection['client']].append(rule_co_udp)

    for (key,host) in topo['hosts'].items():
        rules = rules_dict[key]
        with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']), shell=host['shell'], warn_only=env.warnOnly):
            sudo('iptables-save > /root/dsl.fw')
            sudo('iptables -F; iptables -X; iptables -Z; iptables -N P2P')
            for rule in rules:
                sudo(rule, host['shell'])

def before_run_test_windows(run_id):
    topo = load_topo(run_id)
    local('rm ./tmp/%s.* -f'%run_id)
    local('mkdir tmp -p')
    dump_filter=''
    for (cid,connection) in topo['connections'].items():
        if connection['type']=='Test':
            if dump_filter != '':
                dump_filter += ' or ' 
            dump_filter += '(port %s)' % connection['port']

    for (host_id, host) in topo['hosts'].items():
        with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']),shell=host['shell']):
            tshark_pids = run('ps aux | grep windump | awk "{print $1}"')
            for pid in tshark_pids.splitlines():
                print ('windump:%s'%pid)
                if pid:
                    run('kill %s'%pid)
            tshark_pid = run('./StartTshark.sh %s \"%s\"' % (run_id,dump_filter))
            topo['hosts'][host_id]['tshark_pid'] = tshark_pid
    save_topo(topo, run_id)

def after_run_test(run_id):
    topo = load_topo(run_id)
    logs = pys.dump.collect_log_in_topo(topo)
    active_datas = pys.dump.analysis_logs(logs)

    outputs = []
    for (key,host) in topo['hosts'].items():
        with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']), shell=host['shell']):
            outputs.append(sudo('iptables -L -nvx'))
            sudo('iptables-restore < /root/dsl.fw')

    passive_datas = pys.dump.dump_iptable(outputs)
    pys.dump.passive_merge_active(passive_datas, active_datas, '%s.csv'%topo['runId'])
    local('rm ./tmp/%s.* -f'%run_id)

def after_run_test_windows(run_id):
    topo = load_topo(run_id)
    logs = pys.dump.collect_log_in_topo(topo)
    active_datas = pys.dump.analysis_logs(logs)

    tcp_outputs={}
    udp_outputs={}
    for (host_id, host) in topo['hosts'].items():
        with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']),shell=host['shell']):
            run('kill %s'%host['tshark_pid'])
            tcp_output = run('tshark -r ./%s.pcap -z conv,tcp -n -q 2>/dev/null' % run_id, shell=True)
            tcp_outputs[host_id]=tcp_output
            udp_output = run('tshark -r ./%s.pcap -z conv,udp -n -q 2>/dev/null' % run_id, shell=True)
            udp_outputs[host_id]=udp_output

    passive_datas=pys.dump.dump_pcap(tcp_outputs, topo, 'tcp')
    passive_datas=dict(passive_datas,**(pys.dump.dump_pcap(udp_outputs, topo, 'udp')))
    print ('==============================')
    for (k,v) in passive_datas.items():
        print k
        print v
    pys.dump.passive_merge_active(passive_datas, active_datas, '%s.csv'%topo['runId'])
    local('rm ./tmp/%s.* -f'%run_id)

def run_step(step, topo):
    connection_ids = step['connections']
    if 'network-loads' in step:
        iperf_hosts={}

        for (hid,host) in topo['hosts'].items():
            with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']),shell=host['shell'],warn_only=True):
                if 'cmd.exe' in host['shell']:
                    server_pids = run('ps aux | grep %sServer | awk "{print $1}"'%topo['protocol'])
                    for pid in server_pids.splitlines():
                        print ('%sServer:%s'%(topo['protocol'],pid))
                        if pid:
                            run('kill %s'%pid)
                    stress_pids = run('ps aux | grep bash | awk "{print $1}"')
                    for pid in server_pids.splitlines():
                        print ('bash:%s'%pid)
                        if pid:
                            run('kill %s >/dev/null'%pid,pty=False)
                    iperf_pids = run('ps aux | grep iperf | awk "{print $1}"') 
                    for pid in iperf_pids.splitlines():
                        if pid:
                            run('kill %s'%pid)
                else:
                    run('killall -9 -HUP iperf >/dev/null')
                    run('killall -9 -HUP TCPServer >/dev/null')
                    run('killall -9 -HUP loop >/dev/null')

        for load_id in step['network-loads']:
            load = topo['network-loads'][load_id]
            server=topo['hosts'][load['server']] 
            client=topo['hosts'][load['client']] 

            with settings(host_string='test@%s:%s'%(server['login_ip'],server['login_port']),shell=server['shell']):
                sid = run('./StartIperf.sh -s %s'%load['protocol'],pty=False)
                iperf_hosts.setdefault(load['server'],[])
                iperf_hosts[load['server']].append(sid)

            with settings(host_string='test@%s:%s'%(client['login_ip'],client['login_port']),shell=client['shell']):
                cid = run('./StartIperf.sh -c %s %s'%(load['protocol'],server['ip']),pty=False)
                iperf_hosts.setdefault(load['client'],[])
                iperf_hosts[load['client']].append(cid)

    def run_connection_server(connection, topo):
        server_host = topo['hosts'][connection['server']]
        server_host_ip = server_host['login_ip']
        server_host_port = server_host['login_port']
        server_ip = server_host['ip']
        client_ip = topo['hosts'][connection['client']]['ip']
        connection_port = connection['port']
        run_id = topo['runId']
        data_size = connection['bytes']
        shell = server_host['shell']
        protocol = connection['protocol']
        print 'data size %d'% int(data_size)
        if int(data_size) > 0:
            command='./ServerRecv.sh %s %s %s %s %s'%(server_ip,client_ip, connection_port,run_id,protocol)
        else:
            command='./ServerSend.sh %s %s %s %s %s %s'%(server_ip,client_ip, connection_port,run_id,data_size.strip('-')
, protocol)
        with settings(host_string='test@%s:%s'%(server_host_ip,server_host_port), shell=shell):
            output=run(command,pty=False)
            lines = output.split('\n')
            result_dict={}
            for line in lines:
                words = line.split(':')
                result_dict[words[0]] = words[1]
        return result_dict

    def run_connection_client(connection, topo):
        client_host = topo['hosts'][connection['client']]
        client_host_ip = client_host['login_ip']
        client_host_port = client_host['login_port']
        client_ip = client_host['ip']
        server_ip = topo['hosts'][connection['server']]['ip']
        connection_port = connection['port']
        run_id = topo['runId']
        data_size = connection['bytes']
        shell = client_host['shell']
        protocol = connection['protocol']
#        if connection['type'] == 'Test':
#            thread_count = 1
#        else:
#            thread_count = connection['thread-count']
        if int(data_size) > 0:
            command='./ClientSend.sh %s %s %s %s %s %s'%(client_ip,server_ip,connection_port,run_id,data_size,protocol)
        else:
            command='./ClientRecv.sh %s %s %s %s %s'%(client_ip,server_ip,connection_port,run_id,protocol)
        with settings(host_string='test@%s:%s'%(client_host_ip, client_host_port), shell=shell):
            output = run(command, pty=False)
            lines = output.split('\n')
            result_dict={}
            for line in lines:
                words = line.split(':')
                result_dict[words[0]]=words[1]
        return result_dict

    processes_on_hosts = topo['hosts']
    client_processes = {}
    connection_tokens={}

    stressor_begin_time=time.time()
    stressor_work_time=0
    for (host_id,stress_time) in step['stressed_hosts']:
        with settings(host_string='test@%s:%s'%(topo['hosts'][host_id]['login_ip'], topo['hosts'][host_id]['login_port']), shell=topo['hosts'][host_id]['shell'],warn_only=env.warnOnly):
            pids = run('./stress.sh',pty=False).splitlines()
            topo['hosts'][host_id]['cpu_pids']=pids
#            print 'stress pids:'
#            print pids
            if stressor_work_time < stress_time:
                stressor_work_time = int(stress_time)
            print ('=================Watch %s  CPU=========================='%topo['hosts'][host_id]['ip'])
   
    for cid in connection_ids:
        connection = topo['connections'][cid]
        result_dict = run_connection_server(connection, topo)
        host_id = connection['server'] 
        processes_on_hosts[host_id].setdefault('server-processes',[])
        processes_on_hosts[host_id]['server-processes'].append({'token':result_dict['token'],'pid':result_dict['pid']})
        connection_tokens[cid]=result_dict['token']

    for cid in sorted(connection_ids):
        print 'run connection %s'% cid
        connection = topo['connections'][cid]
        result_dict = run_connection_client(connection, topo)
        host_id = connection['client']
        processes_on_hosts[host_id].setdefault('client-processes',[])
        processes_on_hosts[host_id]['client-processes'].append({'token':result_dict['token'],'pid':result_dict['pid']})
        client_processes[result_dict['token']]=result_dict['pid']

    i = 1
    loop_times = 100
    loop_interval = 1

    def isProcessOver(pid, shell, keyword=None):
        if 'cmd.exe' in shell:
            lines = run('ps').split('\n')
            for line in lines:
                try:
                    if line.split()[0] == pid:
                        return False
                except IndexError:
                    return True
            return True 
        else:
            return  run('./IsProcessOver.sh %s'%pid)=='stopped'

    while i<=loop_times:
        if len(client_processes) == 0:
            break
        for (hid, host) in processes_on_hosts.items():
            if 'client-processes' in host:
                with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']), shell=host['shell'],warn_only=env.warnOnly):
                    with hide('output','running','stdout'):
                        still_running_client_processes = []
                        for pair in host['client-processes']:
                            token = pair['token']
                            pid = pair['pid']
                            if isProcessOver(pid, host['shell'])==True:
                                client_processes.pop(token, None)
                            else:
                                still_running_client_processes.append(pair)
                        host['client-processes']=still_running_client_processes
        print '========================= %d =============================' %(i*loop_interval)
        time.sleep(loop_interval)
        i += 1
    for (hid, host) in processes_on_hosts.items():
        if 'client-processes' in host:
            if len(host['client-processes']) > 0:
                print '   Some clients not over           '
        if 'server-processes' in host:
            with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']), shell=host['shell']):
                for pair in host['server-processes']:
                    token = pair['token']
                    pid = pair['pid']
                    try:
                        run('kill %s'%pid)
                    except BaseException as e:
                        print e
            host['server-processes']=[]

    stressor_elapse_time = time.time() - stressor_begin_time
    print '%s seconds elapse since stressor started'%stressor_elapse_time
#### Replace Waiting for stresstor to stop with kill stressor
    for (host_id,stress_time) in step['stressed_hosts']:
        with settings(host_string='test@%s:%s'%(topo['hosts'][host_id]['login_ip'], topo['hosts'][host_id]['login_port']), shell=topo['hosts'][host_id]['shell'],warn_only=True):
            pids=topo['hosts'][host_id]['cpu_pids']
            print ('kill consumer')
            for pid in pids:
                run('kill %s >/dev/null'%pid)
 
#    if stressor_elapse_time < stressor_work_time:
#        time.sleep(stressor_work_time - stressor_elapse_time)
#        print '=== wait for stressor ==='

    if 'network-loads' in step:
        for (hid,pids) in iperf_hosts.items():
            with settings(host_string='test@%s:%s'%(topo['hosts'][hid]['login_ip'], topo['hosts'][hid]['login_port']), shell=topo['hosts'][hid]['shell'],warn_only=env.warnOnly):
                for pid in pids:
                    print ('kill iperf')
                    run('kill %s'%pid)

    with open('./tmp/%s.tokens.csv' % topo['runId'], 'a+') as cf:
        writer = csv.writer(cf)
        for (connection_id, token) in connection_tokens.items():
            writer.writerow([connection_id, token])
        cf.close()
