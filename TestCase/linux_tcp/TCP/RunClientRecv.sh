#!/bin/bash 

# run client
server_ip=$1
port=$2
thread_count=$3
log_file=../$4
pid_file=../$5
echo 'pid file:'$pid_file
echo 'log file:'$log_file

./TCPClient/TCPClientRecv -i $server_ip -p $port >$log_file 2>&1 &
clientId=$!
if [ $pid_file ]; then
    echo $clientId >> $pid_file
fi
exit
