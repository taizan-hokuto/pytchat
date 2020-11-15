import datetime
import httpx
import json
import os
import re
from .. import config

PATTERN = re.compile(r"(.*)\(([0-9]+)\)$")


def extract(url):
    _session = httpx.Client(http2=True)
    html = _session.get(url, headers=config.headers)
    with open(str(datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                  ) + 'test.json', mode='w', encoding='utf-8') as f:
        json.dump(html.json(), f, ensure_ascii=False)


def save(data, filename, extention) -> str:
    save_filename = filename + "_" + (datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')) + extention
    with open(save_filename ,mode='w', encoding='utf-8') as f:
        f.writelines(data)
    return save_filename


def checkpath(filepath):
    splitter = os.path.splitext(os.path.basename(filepath))
    body = splitter[0]
    extention = splitter[1]
    newpath = filepath
    counter = 1
    while os.path.exists(newpath):
        match = re.search(PATTERN, body)
        if match:
            counter = int(match[2]) + 1
            num_with_bracket = f'({str(counter)})'
            body = f'{match[1]}{num_with_bracket}'
        else:
            body = f'{body}({str(counter)})'
        newpath = os.path.join(os.path.dirname(filepath), body + extention)
    return newpath
