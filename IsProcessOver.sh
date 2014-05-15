#!/bin/bash
pid=$1
if ps -p $pid > /dev/null
then
    echo 'running'
else
    echo 'stopped'
fi

