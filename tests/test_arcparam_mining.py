import pytest
from pytchat.tool.mining import parser
import pytchat.config as config
import requests, json
from pytchat.paramgen import arcparam_mining as arcparam

def test_arcparam_e(mocker):
    try:
        arcparam.getparam("01234567890",-1)
        assert False
    except ValueError:
        assert True

    


def test_arcparam_0(mocker):
    param = arcparam.getparam("01234567890",0)

    assert param =="op2w0wQsGiBDZzhhRFFvTE1ERXlNelExTmpjNE9UQWdBUSUzRCUzREABYARyAggBeAE%3D"


def test_arcparam_1(mocker):
    param = arcparam.getparam("01234567890", seektime = 100000)
    print(param)
    assert param == "op2w0wQzGiBDZzhhRFFvTE1ERXlNelExTmpjNE9UQWdBUSUzRCUzREABWgUQgMLXL2AEcgIIAXgB"

def test_arcparam_2(mocker):
    param = arcparam.getparam("PZz9NB0-Z64",1)
    url=f"https://www.youtube.com/live_chat_replay?continuation={param}&playerOffsetMs=1000&pbj=1"
    resp = requests.Session().get(url,headers = config.headers)
    jsn = json.loads(resp.text)
    _ , chatdata = parser.parse(jsn[1])
    test_id = chatdata[0]["addChatItemAction"]["item"]["liveChatPaidMessageRenderer"]["id"]
    print(test_id)
    assert test_id == "ChwKGkNKSGE0YnFJeWVBQ0ZWcUF3Z0VkdGIwRm9R"

def test_arcparam_3(mocker):
    param = arcparam.getparam("01234567890")
    assert param == "op2w0wQsGiBDZzhhRFFvTE1ERXlNelExTmpjNE9UQWdBUSUzRCUzREABYARyAggBeAE%3D"
