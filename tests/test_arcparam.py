import pytest
from pytchat.parser.replay import Parser
import pytchat.config as config
import requests, json
from pytchat.paramgen import arcparam

def test_arcparam_0(mocker):
    param = arcparam.getparam("01234567890",-1)
    assert "op2w0wRyGjxDZzhhRFFvTE1ERXlNelExTmpjNE9UQWFFLXFvM2JrQkRRb0xNREV5TXpRMU5qYzRPVEFnQVElM0QlM0QoADAAOABAAEgEUhwIABAAGAAgACoOc3RhdGljY2hlY2tzdW1AAFgDYAFoAHIECAEQAHgA" == param


def test_arcparam_1(mocker):
    param = arcparam.getparam("01234567890", seektime = 100000)
    assert "op2w0wR3GjxDZzhhRFFvTE1ERXlNelExTmpjNE9UQWFFLXFvM2JrQkRRb0xNREV5TXpRMU5qYzRPVEFnQVElM0QlM0QogNDbw_QCMAA4AEAASANSHAgAEAAYACAAKg5zdGF0aWNjaGVja3N1bUAAWANgAWgAcgQIARAAeAA%3D" == param

def test_arcparam_2(mocker):
    param = arcparam.getparam("SsjCnHOk-Sk")
    url=f"https://www.youtube.com/live_chat_replay/get_live_chat_replay?continuation={param}&pbj=1"
    resp = requests.Session().get(url,headers = config.headers)
    jsn = json.loads(resp.text)
    parser = Parser()
    _ , chatdata = parser.parse(jsn)
    test_id = chatdata[0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["id"]
    print(test_id)
    assert "CjoKGkNMYXBzZTdudHVVQ0Zjc0IxZ0FkTnFnQjVREhxDSnlBNHV2bnR1VUNGV0dnd2dvZDd3NE5aZy0w" == test_id

def test_arcparam_3(mocker):
    param = arcparam.getparam("01234567890")
    assert "op2w0wRyGjxDZzhhRFFvTE1ERXlNelExTmpjNE9UQWFFLXFvM2JrQkRRb0xNREV5TXpRMU5qYzRPVEFnQVElM0QlM0QoATAAOABAAEgDUhwIABAAGAAgACoOc3RhdGljY2hlY2tzdW1AAFgDYAFoAHIECAEQAHgA" == param
