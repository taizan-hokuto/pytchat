import json
import pytest
import asyncio,aiohttp
from pytchat.parser.live import Parser
from pytchat.processors.compatible.processor import CompatibleProcessor
from pytchat.exceptions import (
    NoLivechatRendererException,NoYtinitialdataException,
    ResponseContextError, NoContentsException)

from pytchat.processors.compatible.renderer.textmessage import LiveChatTextMessageRenderer
from pytchat.processors.compatible.renderer.paidmessage import LiveChatPaidMessageRenderer
from pytchat.processors.compatible.renderer.paidsticker import LiveChatPaidStickerRenderer
from pytchat.processors.compatible.renderer.legacypaid import LiveChatLegacyPaidMessageRenderer

parser = Parser(is_replay=False)

def test_textmessage(mocker):
    '''api互換processorのテスト：通常テキストメッセージ'''
    processor = CompatibleProcessor()

    _json = _open_file("tests/testdata/compatible/textmessage.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id" : "",
        "timeout" : 7,
        "chatdata" : chatdata
    }
    ret = processor.process([data])

    assert ret["kind"]== "youtube#liveChatMessageListResponse"
    assert ret["pollingIntervalMillis"]==data["timeout"]*1000
    assert ret.keys() == {
        "kind",   "etag",   "pageInfo",   "nextPageToken","pollingIntervalMillis","items"
    }
    assert ret["pageInfo"].keys() == {
        "totalResults",   "resultsPerPage"
    }
    assert ret["items"][0].keys() == {
        "kind",   "etag",   "id",   "snippet", "authorDetails"
    }
    assert ret["items"][0]["snippet"].keys() == {
        'type', 'liveChatId', 'authorChannelId', 'publishedAt', 'hasDisplayContent', 'displayMessage', 'textMessageDetails'
    }
    assert ret["items"][0]["authorDetails"].keys() == {
        'channelId', 'channelUrl', 'displayName', 'profileImageUrl', 'isVerified', 'isChatOwner', 'isChatSponsor', 'isChatModerator'
    }
    assert ret["items"][0]["snippet"]["textMessageDetails"].keys() == {
        'messageText'
    }
    assert "LCC." in ret["items"][0]["id"] 
    assert ret["items"][0]["snippet"]["type"]=="textMessageEvent"

def test_newsponcer(mocker):
    '''api互換processorのテスト：メンバ新規登録'''
    processor = CompatibleProcessor()

    _json = _open_file("tests/testdata/compatible/newSponsor.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id" : "",
        "timeout" : 7,
        "chatdata" : chatdata
    }
    ret = processor.process([data])

    assert ret["kind"]== "youtube#liveChatMessageListResponse"
    assert ret["pollingIntervalMillis"]==data["timeout"]*1000
    assert ret.keys() == {
        "kind",   "etag",   "pageInfo",   "nextPageToken","pollingIntervalMillis","items"
    }
    assert ret["pageInfo"].keys() == {
        "totalResults",   "resultsPerPage"
    }
    assert ret["items"][0].keys() == {
        "kind",   "etag",   "id",   "snippet","authorDetails"
    }
    assert ret["items"][0]["snippet"].keys() == {
        'type', 'liveChatId', 'authorChannelId', 'publishedAt', 'hasDisplayContent', 'displayMessage'

    }
    assert ret["items"][0]["authorDetails"].keys() == {
        'channelId', 'channelUrl', 'displayName', 'profileImageUrl', 'isVerified', 'isChatOwner', 'isChatSponsor', 'isChatModerator'
    }
    assert "LCC." in ret["items"][0]["id"] 
    assert ret["items"][0]["snippet"]["type"]=="newSponsorEvent"


def test_superchat(mocker):
    '''api互換processorのテスト：スパチャ'''
    processor = CompatibleProcessor()

    _json = _open_file("tests/testdata/compatible/superchat.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id" : "",
        "timeout" : 7,
        "chatdata" : chatdata
    }
    ret = processor.process([data])

    assert ret["kind"]== "youtube#liveChatMessageListResponse"
    assert ret["pollingIntervalMillis"]==data["timeout"]*1000
    assert ret.keys() == {
        "kind",   "etag",   "pageInfo",   "nextPageToken","pollingIntervalMillis","items"
    }
    assert ret["pageInfo"].keys() == {
        "totalResults",   "resultsPerPage"
    }
    assert ret["items"][0].keys() == {
        "kind",   "etag",   "id",   "snippet", "authorDetails"
    }
    assert ret["items"][0]["snippet"].keys() == {
        'type', 'liveChatId', 'authorChannelId', 'publishedAt', 'hasDisplayContent', 'displayMessage', 'superChatDetails'
    }
    assert ret["items"][0]["authorDetails"].keys() == {
        'channelId', 'channelUrl', 'displayName', 'profileImageUrl', 'isVerified', 'isChatOwner', 'isChatSponsor', 'isChatModerator'
    }
    assert ret["items"][0]["snippet"]["superChatDetails"].keys() == {
        'amountMicros', 'currency', 'amountDisplayString', 'tier', 'backgroundColor'
    }
    assert "LCC." in ret["items"][0]["id"] 
    assert ret["items"][0]["snippet"]["type"]=="superChatEvent"


def _open_file(path):
    with open(path,mode ='r',encoding = 'utf-8') as f:
        return f.read()
