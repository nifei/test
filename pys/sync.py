#!/usr/bin/env python

from __future__ import with_statement
from fabric.api import local, settings, abort, run, cd, sudo, env, roles, hide
from fabric.operations import get,put,open_shell

def deploy_binary(host,port,protocol,shell):
    with settings(host_string='test@%s:%s'%(host,port),shell=shell):
        run('mkdir %s -p'%protocol)
        system_name=run('uname -s')
        if 'Linux' in system_name:
            system='Linux'
        if 'MINGW' in system_name:
            system='Windows'
    with settings(host_string='test@%s:%s'%(host,port),shell=shell):
        run('rm ./TCP/TCPServer/*')
        run('rm ./TCP/TCPClient/*')
        put('/home/test/TCP/TCPServer/TCPServerSend', './TCP/TCPServer/TCPServerSend',mode=0755)
        put('/home/test/TCP/TCPClient/TCPClientRecv', './TCP/TCPClient/TCPClientRecv',mode=0755)
        put('/home/test/TCP/TCPServer/TCPServerRecv', './TCP/TCPServer/TCPServerRecv',mode=0755)
        put('/home/test/TCP/TCPClient/TCPClientSend', './TCP/TCPClient/TCPClientSend',mode=0755)
def deploy(host,port,protocol,shell):
    with settings(host_string='test@%s:%s'%(host,port),shell=shell):
        run('mkdir %s -p'%protocol)
        system_name=run('uname -s')
        if 'Linux' in system_name:
            system='Linux'
        if 'MINGW' in system_name:
            system='Windows'
        
    with settings(host_string='test@%s:%s'%(host,port),shell=shell):
        #universal scripts
        put('/home/test/ServerSend.sh','./',mode=0755)
        put('/home/test/ServerRecv.sh','./',mode=0755)
        put('/home/test/ClientRecv.sh','./',mode=0755)
        put('/home/test/ClientSend.sh','./',mode=0755)
        put('/home/test/KillProcess.sh','./',mode=0755)
        put('/home/test/IsProcessOver.sh','./',mode=0755)
        put('/home/test/stress.sh','./',mode=0755)
        put('/home/test/loop.sh','./',mode=0755)
        put('/home/test/%s/RunServerSend.sh'%protocol, './%s/RunServerSend.sh'%protocol,mode=0755)
        put('/home/test/%s/RunClientSend.sh'%protocol, './%s/RunClientSend.sh'%protocol,mode=0755)
        put('/home/test/%s/RunServerRecv.sh'%protocol, './%s/RunServerRecv.sh'%protocol,mode=0755)
        put('/home/test/%s/RunClientRecv.sh'%protocol, './%s/RunClientRecv.sh'%protocol,mode=0755)
     
    pass
 
def update_from_remote(host,shell):
    with settings(host_string='test@%s'%host,shell=shell):
        get('ServerTest.sh','ServerTest.sh')
        get('ClientTest.sh','ClientTest.sh')
        get('EndServerTest.sh','EndServerTest.sh')
        get('TCP/RunServer.sh','TCP/RunServer.sh')
        get('TCP/RunClient.sh','TCP/RunClient.sh')

