import json
from aioresponses import aioresponses
from pytchat.core_async.livechat import LiveChatAsync
from pytchat.exceptions import ResponseContextError


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


@aioresponses()
def test_Async(*mock):
    vid = '__test_id__'
    _text = _open_file('tests/testdata/paramgen_firstread.json')
    _text = json.loads(_text)
    mock[0].get(
        f"https://www.youtube.com/live_chat?v={vid}&is_popout=1", status=200, body=_text)
    try:
        chat = LiveChatAsync(video_id='__test_id__')
        assert chat.is_alive()
        chat.terminate()
        assert not chat.is_alive()
    except ResponseContextError:
        assert not chat.is_alive()


def test_MultiThread(mocker):
    _text = _open_file('tests/testdata/paramgen_firstread.json')
    _text = json.loads(_text)
    responseMock = mocker.Mock()
    responseMock.status_code = 200
    responseMock.text = _text
    mocker.patch('requests.Session.get').return_value = responseMock
    try:
        chat = LiveChatAsync(video_id='__test_id__')
        assert chat.is_alive()
        chat.terminate()
        assert not chat.is_alive()
    except ResponseContextError:
        chat.terminate()
        assert not chat.is_alive()
