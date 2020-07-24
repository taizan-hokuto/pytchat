from pytchat.tool.videoinfo import VideoInfo
from pytchat.exceptions import InvalidVideoIdException


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def _set_test_data(filepath, mocker):
    _text = _open_file(filepath)
    response_mock = mocker.Mock()
    response_mock.status_code = 200
    response_mock.text = _text
    mocker.patch('requests.get').return_value = response_mock


def test_archived_page(mocker):
    _set_test_data('tests/testdata/videoinfo/archived_page.txt', mocker)
    info = VideoInfo('__test_id__')
    actual_thumbnail_url =  'https://i.ytimg.com/vi/fzI9FNjXQ0o/hqdefault.jpg'
    assert info.video_id == '__test_id__'
    assert info.get_channel_name() == 'GitHub'
    assert info.get_thumbnail() == actual_thumbnail_url
    assert info.get_title() == 'GitHub Arctic Code Vault'
    assert info.get_channel_id() == 'UC7c3Kb6jYCRj4JOHHZTxKsQ'
    assert info.get_duration() == 148


def test_live_page(mocker):
    _set_test_data('tests/testdata/videoinfo/live_page.txt', mocker)
    info = VideoInfo('__test_id__')
    '''live page :duration = 0'''        
    assert info.get_duration() == 0
    assert info.video_id == '__test_id__'
    assert info.get_channel_name() == 'BGM channel'
    assert info.get_thumbnail() == \
        'https://i.ytimg.com/vi/fEvM-OUbaKs/hqdefault_live.jpg'
    assert info.get_title() == (
        'Coffee Jazz Music - Chill Out Lounge Jazz Music Radio'
        ' - 24/7 Live Stream - Slow Jazz')
    assert info.get_channel_id() == 'UCQINXHZqCU5i06HzxRkujfg'


def test_invalid_video_id(mocker):
    '''Test case invalid video_id is specified.'''
    _set_test_data(
        'tests/testdata/videoinfo/invalid_video_id_page.txt', mocker)
    try:
        _ = VideoInfo('__test_id__')
        assert False
    except InvalidVideoIdException:
        assert True


def test_no_info(mocker):
    '''Test case the video page has renderer, but no info.'''
    _set_test_data(
        'tests/testdata/videoinfo/no_info_page.txt', mocker)
    info = VideoInfo('__test_id__')
    assert info.video_id == '__test_id__'
    assert info.get_channel_name() is None
    assert info.get_thumbnail() is None
    assert info.get_title() is None
    assert info.get_channel_id() is None
    assert info.get_duration() is None
