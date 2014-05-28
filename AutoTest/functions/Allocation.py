__author__ = 'test'
import functions.DeviceDB
import types
db = functions.DeviceDB

# @in : @limitations: [{},{},{}...], @count=1
# @out: IDs in DeviceInfo
device_attrbs = ["ID", "STATUS", "IP", "MAC", "NATTYPE", "NAT", "TUNNEL", "PEERID", "SHARED_COUNT"]
def find_device(limitation, count=None):
    filters=[]
    for (key, value) in limitation.items():
        filter = None
        if key not in device_attrbs:
            continue
        if isinstance(value, types.StringType):
            filter = "%s = '%s'"%(key, value)
        elif isinstance(value, types.ListType):
            value_range = ",".join(["'%s'" % attr_value for attr_value in value])
            filter = "%s in (%s)" % (key, value_range)
        elif isinstance(value, types.TupleType):
            if len(value) == 2:
                range_filters = []
                if value[0]:
                    filters.append("%s > %s" % (key, value[0]))
                if value[1]:
                    filters.append("%s < %s" % (key, value[1]))
                filter = " and ".join(filter_item for filter_item in range_filters)
        elif isinstance(value,types.IntType):
            filter = "%s = %d"%(key,value)
        elif isinstance(value, types.FloatType):
            filter = "%s = %f"%(key, value)
        if filter:
            filters.append(filter)
    where_filter = "where %s"%(" and ".join(filter for filter in filters)) if len(filters)>0 else ""
    return db.query_device_ids_by_filter(where_filter, count)

def occupy_devices(device_ids, occupy_type):
    macs = db.query_device_macs(device_ids)
    if occupy_type == "shared":
        ret, reason = db.increase_shared_device(macs)
    elif occupy_type == "exclusive":
        ret, reason = db.lock_exclusive_device(macs)

def release_devices(device_ids):
    macs = db.query_device_macs(device_ids)
    db.release_device(macs)
