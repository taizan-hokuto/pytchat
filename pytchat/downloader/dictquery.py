class DictQuery(dict):
    def get(self, path, default = None):
        keys = path.split("/")
        val = None
        for key in keys:
            if val:
                if key.isdecimal():
                    if isinstance(val,list) and len(val) > int(key):
                        #val=val[int(key)]
                        val=list(val)[int(key)]
                    else:return default
                elif isinstance(val, dict):
                    val = val.get(key, default)
                else:
                    return default
            else:
                val = dict.get(self, key, default)

        return val
 
def find(target,**kwargs):
    for key in kwargs.keys():
        if key == target:
            return kwargs[key]
        if isinstance(kwargs[key], dict):
            res = find(target,**kwargs[key])
        elif isinstance(kwargs[key], list):
            for item in kwargs[key]:
                res = find(target,**item)
    try:            
        return res
    except UnboundLocalError:
        return None

def getid_replay(item):
        return list((list(item['replayChatItemAction']["actions"][0].values())[0])['item'].values())[0]['id']

def getid_realtime(item):
        return list((list(item.values())[0])['item'].values())[0]['id']


def get_timestamp_realtime(item):
        return list((list(item.values())[0])['item'].values())[0]['timestampUsec']


def get_offsettime(item):
        #return item['replayChatItemAction']["actions"][0]["videoOffsetTimeMsec"]
        return item['replayChatItemAction']["videoOffsetTimeMsec"]