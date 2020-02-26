import requests,json,datetime
from .. import config

def extract(url):
    _session = requests.Session()
    html = _session.get(url, headers=config.headers)
    with open(str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                        )+'test.json',mode ='w',encoding='utf-8') as f:
        json.dump(html.json(),f,ensure_ascii=False)


def save(data,filename,extention):
    with open(filename+"_"+(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                            )+extention,mode ='w',encoding='utf-8') as f:
        f.writelines(data)
