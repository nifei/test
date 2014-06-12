__author__ = 'test'

import os

def listFiles(path, ext):
    for root, folders, files in os.walk(path):
        for file in files:
            if file.split('.')[-1] == ext or ext == None:
                fullPath = os.path.join(root, file)
                yield fullPath
                yield '\n------------------------------------\n'
                with open(fullPath, 'r') as f:
                    for line in f.readlines(1000):
                        yield line
                    f.close()
                yield '\n====================================\n'
