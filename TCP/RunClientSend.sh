#!/bin/bash 

server_ip=$1
port=$2
data_size=$3
log_file=../$4
pid_file=../$5

#./TCPClient/TCPClientSend -i $server_ip -p $port -N 1 -n 1 -s $data_size >$log_file 2>&1 &
./TCPClient/TCPClientSend -i $server_ip -p $port -s $data_size >$log_file 2>&1 &
clientId=$!
if [ $pid_file ]; then
    echo $clientId >> $pid_file
fi
exit
