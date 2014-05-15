#!/bin/bash

if [[ $1 == *-h* ]]
then
    echo "./ClientTest.sh client_ip server_ip port run_id data_size protocol"
    exit 1
fi

ip=$1
server_ip=$2
port=$3
run_id=$4
data_size=$5
test_token=$server_ip'_'$ip'_'$port'_'$run_id
protocol=$6

mkdir -p ./$protocol/log
mkdir -p ./$protocol/pid

log_file=./$protocol/log/$test_token.client.log
pid_file=./$protocol/pid/$test_token.pid

cd ./$protocol
./RunClient.sh $server_ip $port $data_size $log_file $pid_file
cd ../

echo "token:"$test_token
echo "pid:"`cat $pid_file`
