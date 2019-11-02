import requests,json,datetime
from .. import config

def download(cls,url):
    _session = requests.Session()
    html = _session.get(url, headers=config.headers)
    with open(str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                        )+'test.json',mode ='w',encoding='utf-8') as f:
        json.dump(html.json(),f,ensure_ascii=False)


def save(cls,data,filename):
    with open(str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                            )+filename,mode ='w',encoding='utf-8') as f:
        f.writelines(data)
