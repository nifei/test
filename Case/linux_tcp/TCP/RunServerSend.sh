#!/bin/bash

port=$1
data_size=$2
pid_file=../$3
server_log_file=../$4
echo 'pid file:'$pid_file

./TCPServer/TCPServerSend -p $port -s $data_size>$server_log_file 2>&1 &
tcpserverId=$!
if [ $2 ];then
    echo $tcpserverId >> $pid_file
fi
exit
