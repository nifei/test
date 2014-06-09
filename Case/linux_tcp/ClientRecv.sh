#!/bin/bash

if [[ $1 == *-h* ]]
then
    echo "./ClientRecv.sh client_ip server_ip port run_id protocol thread_count"
    exit 1
fi

ip=$1
server_ip=$2
port=$3
run_id=$4
test_token=$server_ip'_'$ip'_'$port'_'$run_id
protocol=$5
thread_count=$6

mkdir -p ./$protocol/log
mkdir -p ./$protocol/pid

log_file=./$protocol/log/$test_token.client.log
pid_file=./$protocol/pid/$test_token.client.pid

rm $pid_file -f
rm $log_file -f

cd ./$protocol
./RunClientRecv.sh $server_ip $port $thread_count $log_file $pid_file
cd ../

#echo "./RunClientRecv.sh $server_ip $port $thread_count $log_file $pid_file"

echo "token:"$test_token
echo "pid:"`cat $pid_file`
