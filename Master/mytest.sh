#!/bin/bash

WorkDir="MyWorkDir"
LogDir="Log"

if [[ ! -d "$WorkDir" ]]; then
	mkdir -p "$WorkDir"
fi

cd $WorkDir
if [[ ! -d "$LogDir" ]]; then
	mkdir -p "$LogDir"
fi

var=1
var=$(($var+1))

echo $var | tee "$LogDir/outPut"

