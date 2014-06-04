__author__ = 'test'

import os,pickle

def name_to_context(name):
    file_name = "./context/%s.pkl" % name
    if os.path.isfile(file_name):
        file = open(file_name, 'rb')
        context = pickle.load(file)
        file.close()
    else:
        context = {}
    return context

def context_to_file(context, name):
    file = open('./context/%s.pkl' % name, 'wb')
    pickle.dump(context, file)
    file.close()
