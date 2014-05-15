#!/bin/bash
./wtest.sh 1M-1
sleep 10
./wtest.sh 1M-2
sleep 10
./wtest.sh 1M-3
sleep 10
./wtest.sh 1M-4
sleep 10
./wtest.sh 1M-5
sleep 10
./wtest.sh 1M-6
sleep 10
./wtest.sh 1M-7
sleep 10
./wtest.sh 1M-8
sleep 10
python average.py
