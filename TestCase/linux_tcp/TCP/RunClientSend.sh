#!/bin/bash 

# run client
server_ip=$1
port=$2
data_size=$3
thread_count=$4
log_file=../$5
pid_file=../$6
echo 'pid file:'$pid_file
echo 'log file:'$log_file

./TCPClient/TCPClientSend -i $server_ip -p $port -N 1 -n 1 -s $data_size >$log_file 2>&1 &
clientId=$!
if [ $pid_file ]; then
    echo $clientId >> $pid_file
fi
exit
