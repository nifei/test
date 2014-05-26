#!/bin/bash
protocol=$1
token=$2
pid_file=./$protocol/pid/$token.pid
pid=`cat $pid_file`
if ps -p $pid > /dev/null
then
    echo 'running'
else
    echo 'stopped'
fi
