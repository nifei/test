#!/bin/bash
./loop.sh >./loop.pid 2>&1 &
sleep 1
cat loop.pid
rm loop.pid 
