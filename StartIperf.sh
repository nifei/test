#!/bin/bash

if [[ $1 == '-s' ]]; then
    if [[ $2 == 'TCP' ]];then
        iperf/iperf -s >/dev/null 2>&1 &
    fi
    if [[ $2 == 'UDP' ]]; then
        iperf/iperf -s -u >/dev/null 2>&1 &
    fi
fi
if [[ $1 == '-c' ]]; then
    if [[ $2 == 'TCP' ]];then
        iperf/iperf -c $3 -t 3600 >/dev/null 2>&1 &
    fi
    if [[ $2 == 'UDP' ]]; then
        iperf/iperf -c $3 -u -b 1000000000 -t 3600  >/dev/null 2>&1 &
    fi
fi

echo $!
