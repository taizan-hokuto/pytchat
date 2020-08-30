import json
import httpx
import pytchat.config as config
from pytchat.paramgen import arcparam
from pytchat.parser.live import Parser


def test_arcparam_0(mocker):
    param = arcparam.getparam("01234567890", -1)
    assert param == "op2w0wQmGhxDZzhLRFFvTE1ERXlNelExTmpjNE9UQWdBUT09SARgAXICCAE%3D" 


def test_arcparam_1(mocker):
    param = arcparam.getparam("01234567890", seektime=100000)
    assert param == "op2w0wQtGhxDZzhLRFFvTE1ERXlNelExTmpjNE9UQWdBUT09KIDQ28P0AkgDYAFyAggB"


def test_arcparam_2(mocker):
    param = arcparam.getparam("SsjCnHOk-Sk", seektime=100)
    url = f"https://www.youtube.com/live_chat_replay/get_live_chat_replay?continuation={param}&pbj=1"
    resp = httpx.Client(http2=True).get(url, headers=config.headers)
    jsn = json.loads(resp.text)
    parser = Parser(is_replay=True)
    contents = parser.get_contents(jsn)
    _, chatdata = parser.parse(contents)
    test_id = chatdata[0]["addChatItemAction"]["item"]["liveChatTextMessageRenderer"]["id"]
    assert test_id == "CjoKGkNMYXBzZTdudHVVQ0Zjc0IxZ0FkTnFnQjVREhxDSnlBNHV2bnR1VUNGV0dnd2dvZDd3NE5aZy0w"


def test_arcparam_3(mocker):
    param = arcparam.getparam("01234567890")
    assert param == "op2w0wQmGhxDZzhLRFFvTE1ERXlNelExTmpjNE9UQWdBUT09SARgAXICCAE%3D"
