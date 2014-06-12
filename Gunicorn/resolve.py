__author__ = 'test'
import importlib
import json
import inspect
import config
import os
import functions.Files

UploadPath = config.UploadPath
listFiles = functions.Files.listFiles

def resolve_query_dict(test_case_name):
    script_module = importlib.import_module('scripts.' + test_case_name)
    test_attr = getattr(script_module, 'query_dict')
    return "resolve query:" + test_case_name + '\n' + "query_dict = " + json.dumps(test_attr, indent=4, separators=(',', ':'))

def resolve_deploy_dict(test_case_name):
    script_module = importlib.import_module('scripts.' + test_case_name)
    test_attr = getattr(script_module, 'deploy_dict')
    return "resolve deploy:" + test_case_name + '\n' + "deploy_dict = " + json.dumps(test_attr, indent=4, separators=(',', ':'))

def resolve_step_list(test_case_name):
    script_module = importlib.import_module('scripts.' + test_case_name)
    try:
        test_attr = getattr(script_module, 'step_list')
        class FuncEncoder(json.JSONEncoder):
            def default(self, func):
                return [line.rstrip('\n').replace('\"', ' ') for line in inspect.getsourcelines(func)[0]]
        data = "resolve steps:" + test_case_name + '\n' + "step_list = " + json.dumps(test_attr, cls=FuncEncoder, indent=4, separators=(',', ':'))
    except:
        data = "No steps found, please assign steps to run like this:\n" \
               "def run_server(): \n" \
               "    run_sync(server_id, 'server.sh') \n" \
               "def run_client(): \n" \
               "    run_sync(client_id, 'client.sh') \n" \
               "step_list = [ run_server, run_client ] \n"
    return data

def resolve_shells(test_case_name):
    format_string=listFiles(UploadPath+test_case_name,'sh')
    return ''.join(format_string)

resolve_script_methods = {
    'query': resolve_query_dict,
    'deploy': resolve_deploy_dict,
    'steps': resolve_step_list,
    'shells': resolve_shells
    }
