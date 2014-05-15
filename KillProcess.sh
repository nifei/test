#!/bin/bash
#kill -KILL `ps aux | grep TCPServer| awk '{print $2}'`
#kill -KILL `ps aux | grep TCPClient| awk '{print $2}'`
killall -9 -HUP TCPServer
killall -9 -HUP TCPClient
