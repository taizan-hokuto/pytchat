import json
from pytchat.parser.live import Parser
from pytchat.processors.superchat.calculator import SuperchatCalculator
from pytchat.exceptions import ChatParseException
parse = SuperchatCalculator()._parse


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def load_chatdata(filepath):
    parser = Parser(is_replay=True)
    # print(json.loads(_open_file(filepath)))
    contents = parser.get_contents(json.loads(_open_file(filepath)))[0]
    return parser.parse(contents)[1]


def test_parse_1():
    renderer = {"purchaseAmountText": {"simpleText": "￥2,000"}}
    symbol, amount = parse(renderer)
    assert symbol == '￥'
    assert amount == 2000.0


def test_parse_2():
    renderer = {"purchaseAmountText": {"simpleText": "ABC\x0a200"}}
    symbol, amount = parse(renderer)
    assert symbol == 'ABC\x0a'
    assert amount == 200.0


def test_process_0():
    """
    parse superchat data
    """
    chat_component = {
        'video_id': '',
        'timeout': 10,
        'chatdata': load_chatdata(r"tests/testdata/calculator/superchat_0.json")
    }
    assert SuperchatCalculator().process([chat_component]) == {
        '￥': 6800.0, '€': 2.0}


def test_process_1():
    """
    parse no superchat data
    """
    chat_component = {
        'video_id': '',
        'timeout': 10,
        'chatdata': load_chatdata(r"tests/testdata/calculator/text_only.json")
    }
    assert SuperchatCalculator().process([chat_component]) == {}


def test_process_2():
    """
    try to parse after replay end
    """
    try:
        chat_component = {
            'video_id': '',
            'timeout': 10,
            'chatdata': load_chatdata(r"tests/testdata/calculator/replay_end.json")
        }
        assert False
    except ChatParseException:
        assert True
