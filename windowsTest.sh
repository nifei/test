#!/bin/bash
fab run_test:192.168.91.193,'/bin/bash -l -c',192.168.91.244,'cmd.exe /c c:/msys/bin/sh.exe -l -c',1234,1000,1024,TCP
fab run_test:192.168.91.244,'cmd.exe /c c:/msys/bin/sh.exe -l -c',192.168.91.194,'/bin/bash -l -c',1234,1001,1024,TCP
