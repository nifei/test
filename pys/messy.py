#!/usr/bin/env python
from fabric.api import local, settings, abort, run, cd, sudo, env, roles, hide
import re
import csv


def lookup_dict(result_dict, target_ip, name):
    for x in result_dict.keys():
        if target_ip in x:
            lines=result_dict[x].split('\n')
            for line in lines:
                words=line.split(':') 
                if words[0]==name:
                    return words[1]
    pass

