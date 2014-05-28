#!/bin/bash
protocol=$1
token=$2
pid_file=./$protocol/pid/$token.pid
kill `cat $pid_file`
