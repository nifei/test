__author__ = 'test'

def autoTest():
    # deployment finished
    run(1, "WatchIptables.sh")
    run(1, "StartServer.sh")
    pid = run(2, "StartClient.sh")
    wait(2, pid)
    run(1, "StopServer.sh")

    run(1, "StartServer.sh")
    wait(1, "OK")

    pass

def run(id, script):
    #
    return 0

def wait(id, pid):
    pass
