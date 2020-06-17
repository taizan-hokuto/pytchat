import asyncio
import re
from aioresponses import aioresponses
from concurrent.futures import CancelledError
from pytchat.core_multithread.livechat import LiveChat
from pytchat.core_async.livechat import LiveChatAsync
from pytchat.processors.dummy_processor import DummyProcessor


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


@aioresponses()
def test_async_live_stream(*mock):

    async def test_loop(*mock):
        pattern = re.compile(
            r'^https://www.youtube.com/live_chat/get_live_chat\?continuation=.*$')
        _text = _open_file('tests/testdata/test_stream.json')
        mock[0].get(pattern, status=200, body=_text)
        chat = LiveChatAsync(video_id='', processor=DummyProcessor())
        chats = await chat.get()
        rawdata = chats[0]["chatdata"]
        # assert fetching livachat data
        assert list(rawdata[0]["addChatItemAction"]["item"].keys())[
            0] == "liveChatTextMessageRenderer"
        assert list(rawdata[1]["addChatItemAction"]["item"].keys())[
            0] == "liveChatTextMessageRenderer"
        assert list(rawdata[2]["addChatItemAction"]["item"].keys())[
            0] == "liveChatPlaceholderItemRenderer"
        assert list(rawdata[3]["addLiveChatTickerItemAction"]["item"].keys())[
            0] == "liveChatTickerPaidMessageItemRenderer"
        assert list(rawdata[4]["addChatItemAction"]["item"].keys())[
            0] == "liveChatPaidMessageRenderer"
        assert list(rawdata[5]["addChatItemAction"]["item"].keys())[
            0] == "liveChatPaidStickerRenderer"
        assert list(rawdata[6]["addLiveChatTickerItemAction"]["item"].keys())[
            0] == "liveChatTickerSponsorItemRenderer"

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_loop(*mock))
    except CancelledError:
        assert True


@aioresponses()
def test_async_replay_stream(*mock):

    async def test_loop(*mock):
        pattern_live = re.compile(
            r'^https://www.youtube.com/live_chat/get_live_chat\?continuation=.*$')
        pattern_replay = re.compile(
            r'^https://www.youtube.com/live_chat_replay/get_live_chat_replay\?continuation=.*$')
        # empty livechat -> switch to fetch replaychat
        _text_live = _open_file('tests/testdata/finished_live.json')
        _text_replay = _open_file('tests/testdata/chatreplay.json')
        mock[0].get(pattern_live, status=200, body=_text_live)
        mock[0].get(pattern_replay, status=200, body=_text_replay)

        chat = LiveChatAsync(video_id='', processor=DummyProcessor())
        chats = await chat.get()
        rawdata = chats[0]["chatdata"]
        # assert fetching replaychat data
        assert list(rawdata[0]["addChatItemAction"]["item"].keys())[
            0] == "liveChatTextMessageRenderer"
        assert list(rawdata[14]["addChatItemAction"]["item"].keys())[
            0] == "liveChatPaidMessageRenderer"

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_loop(*mock))
    except CancelledError:
        assert True


@aioresponses()
def test_async_force_replay(*mock):

    async def test_loop(*mock):
        pattern_live = re.compile(
            r'^https://www.youtube.com/live_chat/get_live_chat\?continuation=.*$')
        pattern_replay = re.compile(
            r'^https://www.youtube.com/live_chat_replay/get_live_chat_replay\?continuation=.*$')
        # valid live data, but force_replay = True
        _text_live = _open_file('tests/testdata/test_stream.json')
        # valid replay data
        _text_replay = _open_file('tests/testdata/chatreplay.json')

        mock[0].get(pattern_live, status=200, body=_text_live)
        mock[0].get(pattern_replay, status=200, body=_text_replay)
        # force replay
        chat = LiveChatAsync(
            video_id='', processor=DummyProcessor(), force_replay=True)
        chats = await chat.get()
        rawdata = chats[0]["chatdata"]
        # assert fetching replaychat data
        assert list(rawdata[14]["addChatItemAction"]["item"].keys())[
            0] == "liveChatPaidMessageRenderer"
        # assert not mix livechat data
        assert list(rawdata[2]["addChatItemAction"]["item"].keys())[
            0] != "liveChatPlaceholderItemRenderer"

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_loop(*mock))
    except CancelledError:
        assert True


def test_multithread_live_stream(mocker):

    _text = _open_file('tests/testdata/test_stream.json')
    responseMock = mocker.Mock()
    responseMock.status_code = 200
    responseMock.text = _text
    mocker.patch(
        'requests.Session.get').return_value.__enter__.return_value = responseMock

    chat = LiveChat(video_id='test_id', processor=DummyProcessor())
    chats = chat.get()
    rawdata = chats[0]["chatdata"]
    # assert fetching livachat data
    assert list(rawdata[0]["addChatItemAction"]["item"].keys())[
        0] == "liveChatTextMessageRenderer"
    assert list(rawdata[1]["addChatItemAction"]["item"].keys())[
        0] == "liveChatTextMessageRenderer"
    assert list(rawdata[2]["addChatItemAction"]["item"].keys())[
        0] == "liveChatPlaceholderItemRenderer"
    assert list(rawdata[3]["addLiveChatTickerItemAction"]["item"].keys())[
        0] == "liveChatTickerPaidMessageItemRenderer"
    assert list(rawdata[4]["addChatItemAction"]["item"].keys())[
        0] == "liveChatPaidMessageRenderer"
    assert list(rawdata[5]["addChatItemAction"]["item"].keys())[
        0] == "liveChatPaidStickerRenderer"
    assert list(rawdata[6]["addLiveChatTickerItemAction"]["item"].keys())[
        0] == "liveChatTickerSponsorItemRenderer"
    chat.terminate()
