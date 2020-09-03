import asyncio
import json
from pytest_httpx import HTTPXMock
from concurrent.futures import CancelledError
from pytchat.core_multithread.livechat import LiveChat
from pytchat.core_async.livechat import LiveChatAsync
from pytchat.exceptions import ResponseContextError


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def add_response_file(httpx_mock: HTTPXMock, jsonfile_path: str):
    testdata = json.loads(_open_file(jsonfile_path))
    httpx_mock.add_response(json=testdata)


def test_async(httpx_mock: HTTPXMock):
    add_response_file(httpx_mock, 'tests/testdata/paramgen_firstread.json')

    async def test_loop():
        try:
            chat = LiveChatAsync(video_id='__test_id__')
            _ = await chat.get()
            assert chat.is_alive()
            chat.terminate()
            assert not chat.is_alive()
        except ResponseContextError:
            assert False
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_loop())
    except CancelledError:
        assert True


def test_multithread(httpx_mock: HTTPXMock):
    add_response_file(httpx_mock, 'tests/testdata/paramgen_firstread.json')
    try:
        chat = LiveChat(video_id='__test_id__')
        _ = chat.get()
        assert chat.is_alive()
        chat.terminate()
        assert not chat.is_alive()
    except ResponseContextError:
        assert False
