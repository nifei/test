#!/bin/bash 

server_ip=$1
port=$2
log_file=../$3
pid_file=../$4

./TCPClient/TCPClientRecv -i $server_ip -p $port >$log_file 2>&1 &
clientId=$!
if [ $pid_file ]; then
    echo $clientId >> $pid_file
fi
exit
