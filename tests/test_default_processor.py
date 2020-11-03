import json
from pytchat.parser.live import Parser
from pytchat.processors.default.processor import DefaultProcessor


def test_textmessage(mocker):
    '''text message'''
    processor = DefaultProcessor()
    parser = Parser(is_replay=False)
    _json = _open_file("tests/testdata/default/textmessage.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id": "",
        "timeout": 7,
        "chatdata": chatdata
    }

    ret = processor.process([data]).items[0]
    assert ret.id == "dummy_id"
    assert ret.message == "dummy_message"
    assert ret.timestamp == 1570678496000
    assert ret.datetime == "2019-10-10 12:34:56"
    assert ret.author.name == "author_name"
    assert ret.author.channelId == "author_channel_id"
    assert ret.author.channelUrl == "http://www.youtube.com/channel/author_channel_id"
    assert ret.author.imageUrl == "https://yt3.ggpht.com/------------/AAAAAAAAAAA/AAAAAAAAAAA/xxxxxxxxxxxx/s64-x-x-xx-xx-xx-c0xffffff/photo.jpg"
    assert ret.author.badgeUrl == ""
    assert ret.author.isVerified is False
    assert ret.author.isChatOwner is False
    assert ret.author.isChatSponsor is False
    assert ret.author.isChatModerator is False


def test_textmessage_replay_member(mocker):
    '''text message replay member'''
    processor = DefaultProcessor()
    parser = Parser(is_replay=True)
    _json = _open_file("tests/testdata/default/replay_member_text.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id": "",
        "timeout": 7,
        "chatdata": chatdata
    }
    
    ret = processor.process([data]).items[0]
    assert ret.type == "textMessage"
    assert ret.id == "dummy_id"
    assert ret.message == "dummy_message"
    assert ret.messageEx == ["dummy_message"]
    assert ret.timestamp == 1570678496000
    assert ret.datetime == "2019-10-10 12:34:56"
    assert ret.elapsedTime == "1:23:45"
    assert ret.author.name == "author_name"
    assert ret.author.channelId == "author_channel_id"
    assert ret.author.channelUrl == "http://www.youtube.com/channel/author_channel_id"
    assert ret.author.imageUrl == "https://yt3.ggpht.com/------------/AAAAAAAAAAA/AAAAAAAAAAA/xxxxxxxxxxxx/s64-x-x-xx-xx-xx-c0xffffff/photo.jpg"
    assert ret.author.badgeUrl == "https://yt3.ggpht.com/X=s16-c-k"
    assert ret.author.isVerified is False
    assert ret.author.isChatOwner is False
    assert ret.author.isChatSponsor is True
    assert ret.author.isChatModerator is False


def test_superchat(mocker):
    '''superchat'''
    processor = DefaultProcessor()
    parser = Parser(is_replay=False)
    _json = _open_file("tests/testdata/default/superchat.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id": "",
        "timeout": 7,
        "chatdata": chatdata
    }
    
    ret = processor.process([data]).items[0]
    assert ret.type == "superChat"
    assert ret.id == "dummy_id"
    assert ret.message == "dummy_message"
    assert ret.messageEx == ["dummy_message"]
    assert ret.timestamp == 1570678496000
    assert ret.datetime == "2019-10-10 12:34:56"
    assert ret.elapsedTime == ""
    assert ret.amountValue == 800
    assert ret.amountString == "￥800"
    assert ret.currency == "JPY"
    assert ret.bgColor == 4280150454
    assert ret.author.name == "author_name"
    assert ret.author.channelId == "author_channel_id"
    assert ret.author.channelUrl == "http://www.youtube.com/channel/author_channel_id"
    assert ret.author.imageUrl == "https://yt3.ggpht.com/------------/AAAAAAAAAAA/AAAAAAAAAAA/xxxxxxxxxxxx/s64-x-x-xx-xx-xx-c0xffffff/photo.jpg"
    assert ret.author.badgeUrl == ""
    assert ret.author.isVerified is False
    assert ret.author.isChatOwner is False
    assert ret.author.isChatSponsor is False
    assert ret.author.isChatModerator is False
    assert ret.colors.headerBackgroundColor == 4278239141
    assert ret.colors.headerTextColor == 4278190080
    assert ret.colors.bodyBackgroundColor == 4280150454
    assert ret.colors.bodyTextColor == 4278190080
    assert ret.colors.authorNameTextColor == 2315255808
    assert ret.colors.timestampColor == 2147483648


def test_supersticker(mocker):
    '''supersticker'''
    processor = DefaultProcessor()
    parser = Parser(is_replay=False)
    _json = _open_file("tests/testdata/default/supersticker.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id": "",
        "timeout": 7,
        "chatdata": chatdata
    }
   
    ret = processor.process([data]).items[0]
    assert ret.type == "superSticker"
    assert ret.id == "dummy_id"
    assert ret.message == ""
    assert ret.messageEx == []
    assert ret.timestamp == 1570678496000
    assert ret.datetime == "2019-10-10 12:34:56"
    assert ret.elapsedTime == ""
    assert ret.amountValue == 200
    assert ret.amountString == "￥200"
    assert ret.currency == "JPY"
    assert ret.bgColor == 4278237396
    assert ret.sticker == "https://lh3.googleusercontent.com/param_s=s72-rp"
    assert ret.author.name == "author_name"
    assert ret.author.channelId == "author_channel_id"
    assert ret.author.channelUrl == "http://www.youtube.com/channel/author_channel_id"
    assert ret.author.imageUrl == "https://yt3.ggpht.com/------------/AAAAAAAAAAA/AAAAAAAAAAA/xxxxxxxxxxxx/s64-x-x-xx-xx-xx-c0xffffff/photo.jpg"
    assert ret.author.badgeUrl == ""
    assert ret.author.isVerified is False
    assert ret.author.isChatOwner is False
    assert ret.author.isChatSponsor is False
    assert ret.author.isChatModerator is False
    assert ret.colors.backgroundColor == 4278237396
    assert ret.colors.moneyChipBackgroundColor == 4278248959
    assert ret.colors.moneyChipTextColor == 4278190080
    assert ret.colors.authorNameTextColor == 3003121664


def test_sponsor(mocker):
    '''sponsor(membership)'''
    processor = DefaultProcessor()
    parser = Parser(is_replay=False)
    _json = _open_file("tests/testdata/default/newSponsor_current.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id": "",
        "timeout": 7,
        "chatdata": chatdata
    }
    
    ret = processor.process([data]).items[0]
    assert ret.type == "newSponsor"
    assert ret.id == "dummy_id"
    assert ret.message == "新規メンバー"
    assert ret.messageEx == ["新規メンバー"]
    assert ret.timestamp == 1570678496000
    assert ret.datetime == "2019-10-10 12:34:56"
    assert ret.elapsedTime == ""
    assert ret.bgColor == 0
    assert ret.author.name == "author_name"
    assert ret.author.channelId == "author_channel_id"
    assert ret.author.channelUrl == "http://www.youtube.com/channel/author_channel_id"
    assert ret.author.imageUrl == "https://yt3.ggpht.com/------------/AAAAAAAAAAA/AAAAAAAAAAA/xxxxxxxxxxxx/s64-x-x-xx-xx-xx-c0xffffff/photo.jpg"
    assert ret.author.badgeUrl == "https://yt3.ggpht.com/X=s32-c-k"
    assert ret.author.isVerified is False
    assert ret.author.isChatOwner is False
    assert ret.author.isChatSponsor is True
    assert ret.author.isChatModerator is False


def test_sponsor_legacy(mocker):
    '''lagacy sponsor(membership)'''
    processor = DefaultProcessor()
    parser = Parser(is_replay=False)
    _json = _open_file("tests/testdata/default/newSponsor_lagacy.json")

    _, chatdata = parser.parse(parser.get_contents(json.loads(_json)))
    data = {
        "video_id": "",
        "timeout": 7,
        "chatdata": chatdata
    }
    
    ret = processor.process([data]).items[0]
    assert ret.type == "newSponsor"
    assert ret.id == "dummy_id"
    assert ret.message == "新規メンバー / ようこそ、author_name！"
    assert ret.messageEx == ["新規メンバー / ようこそ、author_name！"]
    assert ret.timestamp == 1570678496000
    assert ret.datetime == "2019-10-10 12:34:56"
    assert ret.elapsedTime == ""
    assert ret.bgColor == 0
    assert ret.author.name == "author_name"
    assert ret.author.channelId == "author_channel_id"
    assert ret.author.channelUrl == "http://www.youtube.com/channel/author_channel_id"
    assert ret.author.imageUrl == "https://yt3.ggpht.com/------------/AAAAAAAAAAA/AAAAAAAAAAA/xxxxxxxxxxxx/s64-x-x-xx-xx-xx-c0xffffff/photo.jpg"
    assert ret.author.badgeUrl == ""
    assert ret.author.isVerified is False
    assert ret.author.isChatOwner is False
    assert ret.author.isChatSponsor is True
    assert ret.author.isChatModerator is False


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()
