#!/bin/bash

if [[ $1 == *-h* ]]
then
    echo "./ServerSend.sh server_ip client_ip port run_id data_size protocol"
    exit 1
fi
ip=$1
clientIp=$2
port=$3
run_id=$4
data_size=$5
protocol=$6

mkdir ./$protocol/pid -p
mkdir ./$protocol/log -p

test_token=$ip'_'$clientIp'_'$port'_'$run_id
pid_file=./$protocol/pid/$ip'_'$clientIp'_'$port'_'$run_id.pid
server_log_file=./$protocol/log/$test_token.server.log

rm $pid_file -f
rm $server_log_file -f

cd ./$protocol
./RunServerSend.sh $port $data_size $pid_file $server_log_file
cd ../

echo "token:"$test_token
echo "pid:"`cat $pid_file`
