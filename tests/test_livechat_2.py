import asyncio
import json
from pytest_httpx import HTTPXMock
from concurrent.futures import CancelledError
from pytchat.core_multithread.livechat import LiveChat
from pytchat.core_async.livechat import LiveChatAsync
from pytchat.processors.dummy_processor import DummyProcessor


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def add_response_file(httpx_mock: HTTPXMock, jsonfile_path: str):
    testdata = json.loads(_open_file(jsonfile_path))
    httpx_mock.add_response(json=testdata)


def test_async_live_stream(httpx_mock: HTTPXMock):
    add_response_file(httpx_mock, 'tests/testdata/test_stream.json')

    async def test_loop():
        chat = LiveChatAsync(video_id='__test_id__', processor=DummyProcessor())
        chats = await chat.get()
        rawdata = chats[0]["chatdata"]
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
        loop.run_until_complete(test_loop())
    except CancelledError:
        assert True




def test_multithread_live_stream(httpx_mock: HTTPXMock):
    add_response_file(httpx_mock, 'tests/testdata/test_stream.json')
    chat = LiveChat(video_id='__test_id__', processor=DummyProcessor())
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
