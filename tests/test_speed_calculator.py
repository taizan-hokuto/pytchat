import json
import pytest
import asyncio,aiohttp
from pytchat.parser.live import Parser
from pytchat.processors.compatible.processor import CompatibleProcessor
from pytchat.exceptions import (
    NoLivechatRendererException,NoYtinitialdataException,
    ResponseContextError, NoContentsException)

from pytchat.processors.speed.calculator import SpeedCalculator

parser = Parser(is_replay =False)

def test_speed_1(mocker):
    '''test speed calculation with normal json.
    test json has 15 chatdata, duration is 30 seconds,
    so the speed of chatdata is 30 chats/minute.
    '''

    processor = SpeedCalculator(capacity=30)

    _json = _open_file("tests/testdata/speed/speedtest_normal.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id" : "",
        "timeout" : 10,
        "chatdata" : chatdata
    }
    ret = processor.process([data])
    assert 30 == ret

def test_speed_2(mocker):
    '''test speed calculation with no valid chat data.
    '''
    processor = SpeedCalculator(capacity=30)

    _json = _open_file("tests/testdata/speed/speedtest_undefined.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id" : "",
        "timeout" : 10,
        "chatdata" : chatdata
    }
    ret = processor.process([data])
    assert 0 == ret
    
def test_speed_3(mocker):
    '''test speed calculation with empty data.
    '''
    processor = SpeedCalculator(capacity=30)

    _json = _open_file("tests/testdata/speed/speedtest_empty.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id" : "",
        "timeout" : 10,
        "chatdata" : chatdata
    }
    ret = processor.process([data])
    assert 0 == ret
    

def _open_file(path):
    with open(path,mode ='r',encoding = 'utf-8') as f:
        return f.read()
