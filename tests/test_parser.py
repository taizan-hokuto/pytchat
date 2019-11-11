import pytest
from pytchat.parser.live import Parser
import json
import asyncio,aiohttp
from aioresponses import aioresponses
from pytchat.exceptions import (
    NoLivechatRendererException,NoYtinitialdataException,
    ResponseContextError, NoContentsException)


def _open_file(path):
    with open(path,mode ='r',encoding = 'utf-8') as f:
        return f.read()
parser = Parser()

@aioresponses()
def test_finishedlive(*mock):
    '''配信が終了した動画を正しく処理できるか'''

    _text = _open_file('tests/testdata/finished_live.json')
    _text = json.loads(_text)

    try:    
        parser.parse(_text)
        assert False
    except NoContentsException:
        assert True

@aioresponses()
def test_parsejson(*mock):
    '''jsonを正常にパースできるか'''

    _text = _open_file('tests/testdata/paramgen_firstread.json')
    _text = json.loads(_text)

    try:    
        parser.parse(_text)
        jsn = _text
        timeout = jsn["response"]["continuationContents"]["liveChatContinuation"]["continuations"][0]["timedContinuationData"]["timeoutMs"]
        continuation = jsn["response"]["continuationContents"]["liveChatContinuation"]["continuations"][0]["timedContinuationData"]["continuation"]
        assert 5035 == timeout
        assert "0ofMyAPiARp8Q2c4S0RRb0xhelJMZDBsWFQwdERkalFhUTZxNXdiMEJQUW83YUhSMGNITTZMeTkzZDNjdWVXOTFkSFZpWlM1amIyMHZiR2wyWlY5amFHRjBQM1k5YXpSTGQwbFhUMHREZGpRbWFYTmZjRzl3YjNWMFBURWdBZyUzRCUzRCiPz5-Os-PkAjAAOABAAUorCAAQABgAIAAqDnN0YXRpY2NoZWNrc3VtOgBAAEoCCAFQgJqXjrPj5AJYA1CRwciOs-PkAli3pNq1k-PkAmgBggEECAEQAIgBAKABjbfnjrPj5AI%3D" == continuation
    except:
        assert False