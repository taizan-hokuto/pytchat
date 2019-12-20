import json
import pytest
import asyncio,aiohttp
from pytchat.parser.live import Parser
from pytchat.processors.compatible.processor import CompatibleProcessor
from pytchat.exceptions import (
    NoLivechatRendererException,NoYtinitialdataException,
    ResponseContextError, NoContentsException)

from pytchat.processors.speed_calculator import SpeedCalculator

parser = Parser()

def test_speed_1(mocker):
    '''test speed normal
    test json has 15 chatdata, duration is 30 seconds,
    so the speed of chatdata is 30 chats/minute.
    '''

    processor = SpeedCalculator(capacity=30,video_id="")

    _json = _open_file("tests/testdata/speed/speedtest1.json")

    _, chatdata = parser.parse(json.loads(_json))
    data = {
        "video_id" : "",
        "timeout" : 10,
        "chatdata" : chatdata
    }
    ret = processor.process([data])
    assert 30 == ret

def test_speed_2(mocker):
    '''test speed with no valid chat data
    
    '''

    processor = SpeedCalculator(capacity=30,video_id="")

    _json = _open_file("tests/testdata/speed/speedtest_none.json")

    _, chatdata = parser.parse(json.loads(_json))
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
