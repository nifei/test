#!/bin/bash

runId=$1
rm $runId.pkl
rm $runId.csv

fabfile=./fabwork.py
fab use_default_topo:$runId-windows
fab before_run_test_windows:$runId-windows
fab run_all_connections:$runId-windows
fab after_run_test_windows:$runId-windows
echo 'windows:'
cat $runId-windows.csv
