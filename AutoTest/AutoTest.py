__author__ = 'test'
import functions.Allocation, functions.Actions
actions = functions.Actions
allocation = functions.Allocation

SHARED_OCCUPIED=(-1, None)
TOTALLY_FREE=0

# device query
query_none = {
    "NAT": ["None", "Cone"],
    "NATTYPE": "yidong",
    "SHARED_COUNT": SHARED_OCCUPIED,
    "STATUS": "Online"
}
query_cone = {
    "NAT": "Cone",
    "SHARED_COUNT": TOTALLY_FREE,
    "STATUS": "Online"
}

def autoTest():
    devices_null_nat = allocation.find_device(query_none, 1)
#    devices_cone_nat = allocation.find_device(query_cone, 1)
#    if len(devices_null_nat) < 1 or len(devices_cone_nat) < 1:
#        return ('Failed', 'No Enough Devices')
    allocation.occupy_devices(devices_null_nat, 'exclusive')
#    allocation.occupy_devices(devices_cone_nat, 'shared')
    deploy_tar = actions.deploy_async(devices_null_nat[0], 'download/windows.zip')
    print "action id:%s, status:%s" % (deploy_tar, actions.wait(deploy_tar))
    deploy_xtar,status = deploy_sync(4, 'download/xtar-win.sh')
    print "action id:%s, status:%s" % (deploy_xtar,status)
    run_xtar,status = run_sync(4, 'download/xtar-win.sh')
    print "action id:%s, status:%s" % (run_xtar, status)
    deploy_tar_l = deploy_async(3, 'download/linux.tar.gz')
    print "action id:%s, status:%s" % (deploy_tar_l, wait(deploy_tar_l))
    deploy_xtar_l,status = deploy_sync(3, 'download/xtar-linux.sh')
    print "action id:%s, status:%s" % (deploy_xtar_l,status)
    run_xtar_l, status = run_sync(3, 'download/xtar-linux.sh')
    print "action id:%s, status:%s" % (run_xtar_l, status)
   allocation.release_devices(devices_null_nat)

autoTest()


