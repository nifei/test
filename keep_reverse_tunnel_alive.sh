#!/bin/bash

COMMAND="ssh test@192.168.91.221 -p 8022 -NfR 8001:127.0.0.1:22"

while : ;
do :
if [ -z $interval ]
then 
    interval=5
fi
if ( pgrep -f -x "$COMMAND" >/dev/null )
then
#    echo "alive:"$interval >> /home/test/interval.log
    interval=$(($interval * 2))
else
    $COMMAND > /home/test/reverse.log 2>&1 
#    echo "dead:"$interval >> /home/test/interval.log
    if [ $interval -ge 2 ]
    then 
        interval=$(($interval / 2))
    fi
fi
sleep $interval
done &
