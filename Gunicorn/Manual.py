__author__ = 'test'

import templates
import functions.DeviceDB, functions.Actions
import cgi
import os
import config
import json

UploadPath = config.UploadPath + 'tmp/'
DownloadPath = config.TestCaseFilesPath + 'tmp/'
LogTargetPath = config.LogTargetPath
LogFilePath = config.LogPath + 'tmp.log'
UploadLogFile = 'upload.sh'
LogFile = config.LogMasterPath + 'tmp.log'

def manualTestPageContent(environ):
    deviceList = functions.DeviceDB.query_all_devices()
    if os.path.exists(UploadPath):
        filelist = os.listdir(UploadPath)
    else:
        filelist = []
        os.mkdir(UploadPath)
    template = templates.get_template( 'ManualTestPage.html' )

    templateVars = {
        'devicelist': deviceList,
        'filelist':filelist
                   }
    return templates.render_template(template, templateVars)

def GetManualTestPage(environ):
    return manualTestPageContent(environ)

def PostManualTestPage(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    fileitem = form['fileUpLoad']
    if fileitem != None:
        file_name = os.path.basename(fileitem.filename)
        local_file = UploadPath + file_name
        open(local_file, 'wb').write(fileitem.file.read())
    return manualTestPageContent(environ)

def PostManualOperation(environ):
    form = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    operation = os.path.basename(environ['PATH_INFO'])
    if operation=='Deploy':
        device_id = int(form['device_id'].value)
        file_name = form['filename'].value
        id = functions.Actions.deploy_async(device_id, DownloadPath + file_name, 0)
        return str(id)
    elif operation=='Execute':
        device_id = int(form['device_id'].value)
        shell = form['script'].value
        local_file = UploadPath + 'tmp.sh'
        open(local_file, 'wb').write(shell)
        id1 = functions.Actions.deploy_async(device_id, DownloadPath +'tmp.sh', 0)
        local_file_2 = UploadPath + 'runtmp.sh'
        rm = 'rm %s'%(LogFilePath)
        mkdir = 'mkdir -p %s'%(config.LogPath)
        run = './tmp.sh >> %s'%(LogFilePath)
        upload = config.SCPLogin%(LogFilePath, config.HostString, config.LogTargetPath)
        open(local_file_2, 'wb').write('\n'.join([rm, mkdir, run, upload]))
        id2 = functions.Actions.deploy_async(device_id, DownloadPath + 'runtmp.sh', 0)
        id3 = functions.Actions.run_async(device_id, 'runtmp.sh', 0)
        return ','.join(str(id) for id in [id1, id2, id3])
    elif operation=='check':
        data = form['data'].value
        ids = [int(id) for id in data.split(',')]
        count = 0
        for id in ids:
            st = functions.DeviceDB.query_action_status(id)
            if st in ['RUNNING', 'PENDING']:
                count += 1
        if count == 0 and len(ids) > 1:
            with open(LogFile, 'r') as f:
                content = '\n'.join(f.readlines(1000))
        else:
            content = str(count)
        return json.dumps({'stop':'true' if count==0 else 'false', 'data':data, 'content':str(content)})
