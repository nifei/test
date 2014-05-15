#!/usr/bin/env python
import re,csv,os
from fabric.api import settings,local
from fabric.operations import get

RE_CHAIN_NAME = re.compile(r'Chain (.+) \(')
RE_SPACE = re.compile(r'\s+')

def dump_iptable(outputs):
    csv_datas = {}
    for output in outputs:
        current_chain = None
        lines = iter(output.splitlines(False))
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = RE_CHAIN_NAME.match(line)
            if match:
                current_chain = match.group(1)
                lines.next() 
                continue
            else:
                if not current_chain:
                    continue
                parts = RE_SPACE.split(line)
                rule = {}
                if len(parts) < 9:
                    continue
                rule['pkts'], rule['bytes'], rule['target'], \
                rule['prot'], rule['opt'], rule['iface_in'], \
                rule['iface_out'], rule['source'], rule['destination'] = parts[:9]
                rule['extra'] = ' '.join(parts[9:])
#udp spt:7002
                port_info_str, port = rule['extra'].split(':')
                port_infos=port_info_str.split()
                protocol=port_infos[0]

                if port_infos[1]=='spt':
                    src_port=port
                    dst_port=None
                elif port_infos[1]=='dpt':
                    src_port=None
                    dst_port=port

                key_data=(rule['source'],src_port,rule['destination'],dst_port,protocol,'data')
                key_conn=(rule['source'],src_port,rule['destination'],dst_port,protocol,'connection')
                csv_datas.setdefault(key_data,{})
                csv_datas.setdefault(key_conn,{})
                if (current_chain == 'INPUT'):
                    (csv_datas[key_data])['@dst']=rule['bytes']
                    (csv_datas[key_conn])['@dst']=rule['bytes']
                if (current_chain == 'OUTPUT'):
                    (csv_datas[key_data])['@src']=rule['bytes']
                    (csv_datas[key_conn])['@src']=rule['bytes']
                continue
    return csv_datas

def dump_pcap(outputs, topo, prot='tcp'):
    finished_connections=[]
    with open('./tmp/%s.tokens.csv' % topo['runId'], 'rb') as cf:
        reader = csv.reader(cf)
        for row in reader:
            finished_connections.append(row[0])
        cf.close()

    LINE_FORMAT = re.compile('(.+):(\d+)\s+<->\s+(.+):(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)')
    def parse_pcap(output,host_ip):
        lines = output.splitlines(False)
        lines = lines[5:-1] # skip head and tail
        connections = {}
        for line in lines:
            src, sport, dst, dport, d2s_frames, d2s_bytes, s2d_frames, s2d_bytes, total_frames, total_bytes = LINE_FORMAT.search(line).groups()
            k1=(src,sport,dst,dport,prot,'connection')
            k2=(src,sport,dst,dport,prot,'data')
            k3=(dst,dport,src,sport,prot,'connection')
            k4=(dst,dport,src,sport,prot,'data')
            if host_ip == src:
                connections[k1]={'@src':s2d_bytes}
                connections[k2]={'@src':s2d_bytes}
                connections[k3]={'@dst':d2s_bytes}
                connections[k4]={'@dst':d2s_bytes}
            if host_ip == dst:
                connections[k1]={'@dst':s2d_bytes}
                connections[k2]={'@dst':s2d_bytes}
                connections[k3]={'@src':d2s_bytes}
                connections[k4]={'@src':d2s_bytes}
        return connections

    merged_connections={}

    for (hid, host) in topo['hosts'].items():
        output = outputs[hid]
        tmp=parse_pcap(output,host['ip'])
        for (k,v) in tmp.items():
            merged_connections.setdefault(k,{})
            merged_connections[k]=dict(merged_connections[k],**v)

    passive_datas={}
    return merged_connections

def passive_merge_active(passive_datas, active_datas, csv_file):
    local('rm %s -f' % csv_file)
#    for key in sorted(active_datas.keys()):
#        print key
#        print active_datas[key]
#    for key in sorted(passive_datas.keys()):
#        print key
#        print passive_datas[key]
    with open('%s' % csv_file, 'a+') as test_summary_file:
        writer = csv.writer(test_summary_file)
        writer.writerow(['connection_id','connection','@src','@dst','bytes','duration','recv/send','valid/recv'])
        def partial_match(key, d):
#possible case: active_key (src,sport,dst,None,'tcp','connection') passive_key (src,sport,dst,dport,'tcp',connection)
            for k, v in d.iteritems():
                if all(k1 == k2 or k2 is None for k1, k2 in zip(k, key)):
                    yield v
        for key in sorted(active_datas.keys()):
            active_data = active_datas[key]
            f_bytes = int(active_data['Bytes'])
            if f_bytes>0 or key[5]=='connection':
                matched_passive_datas=list(partial_match(key,passive_datas))
                for passive_data in matched_passive_datas:
                    connection_id = active_data['connection_id']
                    recv_over_send = 0 if int(passive_data['@src'])==0 else round(float(passive_data['@dst']) / float(passive_data['@src']),4)
                    valid_over_recv = 0 if int(passive_data['@dst'])==0 else round(f_bytes / float(passive_data['@dst']),4)
                    writer.writerow([connection_id,key, passive_data['@src'], passive_data['@dst'], f_bytes, active_data['Duration'],recv_over_send,valid_over_recv])
                
        test_summary_file.close()
        pass

def collect_log_in_topo(topo):
    protocol = topo['protocol']
    if not os.path.isfile('./tmp/%s.tokens.csv' % topo['runId']):
        return None
    logs = {}
    with open('./tmp/%s.tokens.csv' % topo['runId'], 'rb') as cf:
        reader = csv.reader(cf)
        for row in reader:
            token = row[1]
            connection = topo['connections'][row[0]]
            server_log = '%s/log/%s.server.log'%(protocol,token)
            client_log = '%s/log/%s.client.log'%(protocol,token)
            topo['hosts'][connection['server']].setdefault('logs',[])
            topo['hosts'][connection['client']].setdefault('logs',[])
            topo['hosts'][connection['server']].setdefault('load.logs',[])
            topo['hosts'][connection['client']].setdefault('load.logs',[])
            if connection['type'] == 'Test':
                topo['hosts'][connection['server']]['logs'].append(server_log)
                topo['hosts'][connection['client']]['logs'].append(client_log)
                logs.setdefault(row[0],{})
                logs[row[0]]['server'] = server_log
                logs[row[0]]['client'] = client_log
            else:
                topo['hosts'][connection['server']]['load.logs'].append(server_log)
                topo['hosts'][connection['client']]['load.logs'].append(client_log)
        cf.close()
    for (host_id, host) in topo['hosts'].items():
        with settings(host_string='test@%s:%s'%(host['login_ip'],host['login_port']), shell=host['shell']):
            for log in host['logs']:
                get(log,log)
           # for log in host['load.logs']:
           #     get(log,log)
    return logs

def analysis_logs(logs):
    datas={}
    datas_at_server={}
    for (k,v) in logs.items():
        for (role,path) in v.items():
            fn = os.path.basename(path)
            words = fn.split('_')
            server=words[0]
            client=words[1]
            port=words[2]
            words = words[3].split('.')
            runId=words[0]
            role = words[1]

#            key_c2s_tcp = '%s->%s:%s:tcp'%(client,server,port)
#            key_c2s_udp = '%s->%s:%s:udp'%(client,server,port)
#            key_s2c_tcp = '%s->%s:%s:tcp'%(server,client,port)
#            key_s2c_udp = '%s->%s:%s:udp'%(server,client,port)
#            key_c2s_con_tcp = '%s>>%s:%s:tcp'%(client,server,port)
#            key_s2c_con_tcp = '%s>>%s:%s:tcp'%(server,client,port)

            key_c2s_tcp = (client,None,server,port,'tcp','data')
            key_c2s_udp = (client,None,server,port,'udp','data')
            key_s2c_tcp = (server,port,client,None,'tcp','data')
            key_s2c_udp = (server,port,client,None,'udp','data')
            key_c2s_con_tcp = (client,None,server,port,'tcp','connection')
            key_s2c_con_tcp = (server,port,client,None,'tcp','connection')

            cap_keys=['SEND-TCPDATA','RECV-TCPDATA','SEND-UDPDATA','RECV-UDPDATA','CONN-TCP']

# 'SEND/RECV-TCP/UDPDATA' Can be found on both servers and clients, and the unmatched durations are ellimited;
# 'CONN-UDP/TCP' are only found on clients, who establish the connections
 
            with open(path, 'r') as lf:
                for line in lf.readlines():
                    words = line.split(' ')
                    if words[0] not in cap_keys:
                        continue
        
                    if role=='client':
                        if words[0] == 'SEND-TCPDATA':
                            keys = [key_c2s_tcp]
                        elif words[0] == 'RECV-TCPDATA':
                            keys = [key_s2c_tcp]
                        elif words[0] == 'CONN-TCP':
                            keys = [key_c2s_con_tcp, key_s2c_con_tcp]

                        for key in keys:
                            datas.setdefault(key,{'connection_id':k,'Duration':0,'Bytes':0})
                            for word in words[1:]:
                                if ':' in word:
                                    fields=word.split(':')
                                    datas[key][fields[0]]=fields[1]

                    if role=='server':
                        if words[0] == 'SEND-TCPDATA':
                            key=key_s2c_tcp
                        elif words[0] == 'RECV-TCPDATA':
                            key = key_c2s_tcp
                        datas_at_server.setdefault(key,{'connection_id':k,'Duration':0,'Bytes':0})
                        for word in words[1:]:
                            if ':' in word:
                                fileds = word.split(':')
                                datas_at_server[key][fields[0]]=fields[1]

                lf.close()
    for (k,v) in datas.items():
        if v['Bytes']:
            if k in datas_at_server:
                if 'Bytes' in datas_at_server[k]:
                    if datas_at_server[k]['Bytes'] != v['Bytes']:
                        datas[k]['Bytes']='NA'
    return datas
