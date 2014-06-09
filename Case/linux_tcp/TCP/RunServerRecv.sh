#!/bin/bash

port=$1
pid_file=../$2
server_log_file=../$3
echo 'pid file:'$pid_file

./TCPServer/TCPServerRecv -p $port >$server_log_file 2>&1 &
tcpserverId=$!
if [ $2 ];then
    echo $tcpserverId >> $pid_file
fi
exit
