import datetime

def save(data,filename,extention):
    with open(filename+"_"+(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                            )+extention,mode ='w',encoding='utf-8') as f:
        f.writelines(data)

def get_item(dict_body, items: list):
    for item in items:
        if dict_body is None:
            break
        if isinstance(dict_body, dict):
            dict_body = dict_body.get(item)
            continue
        if isinstance(item, int) and \
            isinstance(dict_body, list) and \
            len(dict_body) > item:
            dict_body = dict_body[item]
            continue
        return None
    return dict_body