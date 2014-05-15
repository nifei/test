#!/bin/bash

runId=$1
rm $runId.pkl
rm $runId.csv

fabfile=./fabwork.py

fab use_default_topo:$runId-linux
fab set_host:2,'192.168.44.135','127.0.0.1','8001','/bin/bash -l -c',$runId-linux
fab set_host:1,'192.168.44.147','127.0.0.1','8003','/bin/bash -l -c',$runId-linux
fab before_run_test:$runId-linux
fab run_all_connections:$runId-linux
fab after_run_test:$runId-linux 
echo 'linux:'
cat $runId-linux.csv
