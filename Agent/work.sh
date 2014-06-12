#!/bin/bash
# Get IP
IP=$(ifconfig | grep inet | grep -v "127.0.0.1"| sed -n '1p'| awk '{print $2}'|awk -F ':' '{print $2}')

# Get MAC
MAC=$(ifconfig eth0 | grep HWaddr | awk '{print $5}')

# Get FreeMem
FREEMEM=$(free -m | grep Mem: | awk '{print $4}' | tr -d " ")

# Get FreeDisk
FREEDISK=$(df | grep /dev | awk '{print $4}' | head -1 | tr -d " ")

# Get OSTYPE
OSTYPE=$(cat /proc/version | awk '{print $1}' | tr -d " ")

NETTYPE=`cat Net.conf | grep "NETTYPE:" | awk -F ":" '{print $2}' | tr -d " "`
NAT=`cat Net.conf | grep "NAT:" | awk -F ":" '{print $2}' | tr -d " "`
TUNNEL=`cat Net.conf | grep "TUNNEL:" | awk -F ":" '{print $2}' | tr -d " "`
PEERID=`cat Net.conf | grep "PEERID:" | awk -F ":" '{print $2}' | tr -d " "`
MasterIp=`cat Net.conf | grep "MASTERIP:" | awk -F ":" '{print $2}' | tr -d " "`

# Online login
STATUS="Online"
ACTIONSTATUS="Online"
wget --post-data "STATUS=$STATUS&ACTIONSTATUS=$ACTIONSTATUS&MAC=$MAC&IP=$IP&NETTYPE=$NETTYPE&NAT=$NAT&TUNNEL=$TUNNEL&PEERID=$PEERID&FREEMEM=$FREEMEM&FREEDISK=$FREEDISK&OSTYPE=$OSTYPE" http://$MasterIp/login.php -O login.php 
#rm result.php

# report STATUS, IP, NETTYPE... which may be changed; request ACTION.

unset fileName
unset ACTION
STATUS="Idle"
Download="download";
ACTION_ID=0;

if [[ ! -d "$Download" ]]; then
	mkdir -p "$Download"
fi

CurrentDir=`pwd`
echo $CurrentDir

while true
do
	cd $CurrentDir
# Get NETTYPE
	NETTYPE=`cat Net.conf | grep "NETTYPE:" | awk -F ":" '{print $2}' | tr -d " "`
	NAT=`cat Net.conf | grep "NAT:" | awk -F ":" '{print $2}' | tr -d " "`
	TUNNEL=`cat Net.conf | grep "TUNNEL:" | awk -F ":" '{print $2}' | tr -d " "`
	PEERID=`cat Net.conf | grep "PEERID:" | awk -F ":" '{print $2}' | tr -d " "`
# Get IP
	IP=`ifconfig | grep inet | grep -v "127.0.0.1"| sed -n '1p'| awk '{print $2}'|awk -F ':' '{print $2}'`

# report STATUS, IP, NETTYPE... which may be changed.

#    echo "wget --post-data STATUS=$STATUS&MAC=$MAC&IP=$IP&NETTYPE=$NETTYPE&NAT=$NAT&TUNNEL=$TUNNEL&ACTION_ID=$ACTION_ID http://$MasterIp/action.php -O action.php"

	wget --post-data "STATUS=$STATUS&ACTIONSTATUS=$ACTIONSTATUS&MAC=$MAC&IP=$IP&NETTYPE=$NETTYPE&NAT=$NAT&TUNNEL=$TUNNEL&ACTION_ID=$ACTION_ID&PEERID=$PEERID&FREEMEM=$FREEMEM&FREEDISK=$FREEDISK&OSTYPE=$OSTYPE" http://$MasterIp/action.php -O action.php 

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
		echo "filename: $fileName"
		echo "localFileName: $localFileName"

		if [[ -f "${Download}/${localFileName}" ]]; then
			echo "${Download}/${localFileName} has existed already, Remove firstly." 
			rm -f "${Download}/${localFileName}"
		fi

		wget -c -P "$Download" "http://$MasterIp/$fileName" 

		if [[ ! -f "${Download}/${localFileName}" ]]; then
			STATUS="Disposition_Err"
			ACTIONSTATUS="Disposition_Err"
		else
			STATUS="Disposition_OK"
			ACTIONSTATUS="Disposition_OK"
			chmod a+x "${Download}/${localFileName}"
		fi
		;;
	"EXECUTE")
	fileName=`cat action.php | grep "FILE:" | awk -F ":" '{print $2}' | tr -d " "`
	localFileName="${fileName##*/}"
	cd ${Download}   
	if [[ ! -x "${localFileName}" ]]; then
		if [[ ! -x "${fileName}" ]]; then
			STATUS="ERR1"
			ACTIONSTATUS="Execution_Err"
		else
			."/${fileName}"
			STATUS="OK1"
			ACTIONSTATUS="Execution_OK"
		fi
	else
		filetype=`echo ${localFileName} | awk -F. '{print $NF}'`
		if [[ filetype=='sh' ]]; then
			."/${fileName}"
			STATUS="OK2"
			ACTIONSTATUS="Execution_OK"
		else
			curDir=`pwd`
			dir=$(echo "$localFileName" | awk -F "." '{print $1}')
			if [[ ! -d "$dir" ]]; then
				mkdir -p "$dir"
			fi
			fulldir=$curDir/$dir
			echo $fulldir
			mv $localFileName $fulldir
			cd $fulldir

			if [[ -f "${dir}.sh" ]]; then
				rm -f "${dir}.sh"
			fi

			case  "$localFileName" in
			*.tar)
				tar -xvf $localFileName
				;;
			*.tar.gz)
				tar -zxvf $localFileName
				;;
			*.tgz)
				tar -zxvf $localFileName
				;;
			*.bz2)
				bunzip2 $localFileName
				;;
			*.tar.bz2)
				tar jxvf $localFileName
				;;
			*.bz)
				bunzip2 $localFileName
				;;
			*.tar.bz)
				tar jxvf $localFileName
				;;
			*.zip)
				unzip $localFileName
				;;
			*.gz)
				gzip -d $localFileName
				;;
			*.rar)
				unrar e $localFileName
				;;
			*)
				echo "not compress file"
				;;
			esac
			chmod a+x "${dir}.sh"
			./"${dir}.sh"
			STATUS="Execution_OK"
			ACTIONSTATUS="Execution_OK"
		fi
	fi
	;;
	"REPORTLOG")
		cd $fulldir
		$LogDir=`find . -name "Log" -type d`
		tar -cvzf "${localFileName}.log" $LogDir/*  
		ACTIONSTATU="ReportLog_OK"
#            ACTIONSTATU="ReportLog_Err"
		;;
	*)
		echo "Invalid Action: $ACTION"
		exit 2
		;;
	esac
done

STATUS="Offline"
wget --post-data "STATUS=$STATUS&ACTIONSTATUS=$ACTIONSTATUS&MAC=$MAC&IP=$IP&NETTYPE=$NETTYPE&NAT=$NAT&TUNNEL=$TUNNEL&ACTION_ID=$ACTION_ID" http://$MasterIp/action.php -O action.php
