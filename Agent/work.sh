#!/bin/bash
# Get IP

IP=$(ifconfig | grep inet | grep -v "127.0.0.1"| sed -n '1p'| awk '{print $2}'|awk -F ':' '{print $2}')

# Get MAC
MAC=$(ifconfig eth0 | grep HWaddr | awk '{print $5}')

NATTYPE=`cat Net.conf | grep "NATTYPE:" | awk -F ":" '{print $2}' | tr -d " "`
NAT=`cat Net.conf | grep "NAT:" | awk -F ":" '{print $2}' | tr -d " "`
TUNNEL=`cat Net.conf | grep "TUNNEL:" | awk -F ":" '{print $2}' | tr -d " "`
MasterIp=`cat Net.conf | grep "MASTERIP:" | awk -F ":" '{print $2}' | tr -d " "`

# Online login
STATUS="Online"
wget --post-data "STATUS=$STATUS&MAC=$MAC&IP=$IP&NATTYPE=$NATTYPE&NAT=$NAT&TUNNEL=$TUNNEL" http://$MasterIp/login.php -O login.php 
#rm result.php

# report STATUS, IP, NATTYPE... which may be changed; request ACTION.

unset fileName
unset ACTION
STATUS="Idle"
Download="MyDownload";
ACTION_ID=0;

if [[ ! -d "$Download" ]]; then
    mkdir -p "$Download"
fi

CurrentDir=`pwd`
echo $CurrentDir

while true
do
    cd $CurrentDir
# Get NATTYPE
    NATTYPE=`cat Net.conf | grep "NATTYPE:" | awk -F ":" '{print $2}' | tr -d " "`
    NAT=`cat Net.conf | grep "NAT:" | awk -F ":" '{print $2}' | tr -d " "`
    TUNNEL=`cat Net.conf | grep "TUNNEL:" | awk -F ":" '{print $2}' | tr -d " "`
# Get IP
    IP=`ifconfig | grep inet | grep -v "127.0.0.1"| sed -n '1p'| awk '{print $2}'|awk -F ':' '{print $2}'`

# report STATUS, IP, NATTYPE... which may be changed.

    echo "wget --post-data STATUS=$STATUS&MAC=$MAC&IP=$IP&NATTYPE=$NATTYPE&NAT=$NAT&TUNNEL=$TUNNEL&ACTION_ID=$ACTION_ID http://$MasterIp/action.php -O action.php"

    wget --post-data "STATUS=$STATUS&MAC=$MAC&IP=$IP&NATTYPE=$NATTYPE&NAT=$NAT&TUNNEL=$TUNNEL&ACTION_ID=$ACTION_ID" http://$MasterIp/action.php -O action.php 

# Resolve ACTION, FILE from action.php returned.
	ACTION=`cat action.php | grep "ACTION:" | awk -F ":" '{print $2}' | tr -d " "`
	ACTION_ID=`cat action.php | grep "ACTION_ID:" | awk -F ":" '{print $2}' | tr -d " "`
	EXTRA=`cat action.php | grep "EXTRA:" | awk -F ":" '{print $2}' | tr -d " "`
    echo "ACTION: $ACTION"
    echo "ACTION_ID: $ACTION_ID"
    echo "EXTRA: $EXTRA"

    case "$ACTION" in
        "WAIT")
            sleep 5s
	    STATUS="Idle"
            ;;
        "GET")
            fileName=`cat action.php | grep "FILE:" | awk -F ":" '{print $2}' | tr -d " "`
            localFileName="${fileName##*/}"
#            localFileName=`basename $fileName`
            echo "filename: $fileName"
            echo "localFileName: $localFileName"

            if [[ -f "${Download}/${localFileName}" ]]; then
                echo "${Download}/${localFileName} has existed already, Remove firstly." 
                rm -f "${Download}/${localFileName}"
            fi

            wget -c -P "$Download" "http://$MasterIp/$fileName" 

            if [[ ! -f "${Download}/${localFileName}" ]]; then
                STATUS="Disposition_Err"
            else
                STATUS="Disposition_OK"
                chmod a+x "${Download}/${localFileName}"
            fi
            ;;
        "EXECUTE")
            fileName=`cat action.php | grep "FILE:" | awk -F ":" '{print $2}' | tr -d " "`
            localFileName="${fileName##*/}"
            cd ${Download}   
            if [[ ! -x "${localFileName}" ]]; then
                STATUS="Execution_Err"
            else
                ./${localFileName}
                STATUS="Execution_OK"
            fi
            cd ../
            ;;
        *)
	    
		    echo "Invalid Action: $ACTION"
            exit 2
            ;;
    esac
done

STATUS="Offline"
wget --post-data "STATUS=$STATUS&MAC=$MAC&IP=$IP&NATTYPE=$NATTYPE&NAT=$NAT&TUNNEL=$TUNNEL&ACTION_ID=$ACTION_ID" http://$MasterIp/action.php -O action.php
