#!/bin/bash

cd ./LinuxSrc/LinuxTCP
./make.sh
cd ../../
fab deploy_binary:127.0.0.1,8001,TCP,'/bin/bash -l -c'
fab deploy:127.0.0.1,8001,TCP,'/bin/bash -l -c'
fab deploy_binary:127.0.0.1,8003,TCP,'/bin/bash -l -c'
fab deploy:127.0.0.1,8003,TCP,'/bin/bash -l -c'
#fab deploy:192.168.91.44,22,TCP,'cmd.exe /c c:/msys/1.0/bin/sh.exe -l -c'
#fab deploy:192.168.91.47,22,TCP,'cmd.exe /c c:/msys/1.0/bin/sh.exe -l -c'
