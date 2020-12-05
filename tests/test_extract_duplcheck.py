import json
from pytchat.tool.extract import duplcheck
from pytchat.tool.extract import parser
from pytchat.tool.extract.block import Block
from pytchat.tool.extract.duplcheck import _dump


def _open_file(path):
    with open(path, mode='r', encoding='utf-8') as f:
        return f.read()


def test_overlap():
    """
    test overlap data
        operation : [0]  [2] [3]  [4] -> last :align to end
                    [1] , [5] -> no change

    """

    def load_chatdata(filename):
        return parser.parse(
            json.loads(_open_file(
                "tests/testdata/extract_duplcheck/overlap/" + filename))
        )[1]

    blocks = (
        Block(first=0, last=12771, end=9890,
              chat_data=load_chatdata("dp0-0.json")),
        Block(first=9890, last=15800, end=20244,
              chat_data=load_chatdata("dp0-1.json")),
        Block(first=20244, last=45146, end=32476,
              chat_data=load_chatdata("dp0-2.json")),
        Block(first=32476, last=50520, end=41380,
              chat_data=load_chatdata("dp0-3.json")),
        Block(first=41380, last=62875, end=52568,
              chat_data=load_chatdata("dp0-4.json")),
        Block(first=52568, last=62875, end=54000,
              chat_data=load_chatdata("dp0-5.json"), is_last=True)
    )
    result = duplcheck.remove_overlap(blocks)
    # dp0-0.json has item offset time is 9890 (equals block[0].end = block[1].first),
    # but must be aligne to the most close and smaller value:9779.
    assert result[0].last == 9779

    assert result[1].last == 15800

    assert result[2].last == 32196

    assert result[3].last == 41116

    assert result[4].last == 52384

    # the last block must be always added to result.
    assert result[5].last == 62875


def test_duplicate_head():

    def load_chatdata(filename):
        return parser.parse(
            json.loads(_open_file(
                "tests/testdata/extract_duplcheck/head/" + filename))
        )[1]

    """
    test duplicate head data
        operation : [0] , [1]  -> discard [0]
                    [1] , [2]  -> discard [1]
                    [2] , [3]  -> append  [2]
                    [3] , [4]  -> discard [3]
                    [4] , [5]  -> append  [4]
                    append [5]

        result    : [2] , [4] , [5]
    """

    # chat data offsets are ignored.
    blocks = (
        Block(first=0, last=2500, chat_data=load_chatdata("dp0-0.json")),
        Block(first=0, last=38771, chat_data=load_chatdata("dp0-1.json")),
        Block(first=0, last=45146, chat_data=load_chatdata("dp0-2.json")),
        Block(first=20244, last=60520, chat_data=load_chatdata("dp0-3.json")),
        Block(first=20244, last=62875, chat_data=load_chatdata("dp0-4.json")),
        Block(first=52568, last=62875, chat_data=load_chatdata("dp0-5.json"))
    )
    _dump(blocks)
    result = duplcheck.remove_duplicate_head(blocks)

    assert len(result) == 3
    assert result[0].first == blocks[2].first
    assert result[0].last == blocks[2].last
    assert result[1].first == blocks[4].first
    assert result[1].last == blocks[4].last
    assert result[2].first == blocks[5].first
    assert result[2].last == blocks[5].last


def test_duplicate_tail():
    """
    test duplicate tail data
        operation : append [0]
                    [0] , [1]  -> discard [1]
                    [1] , [2]  -> append  [2]
                    [2] , [3]  -> discard [3]
                    [3] , [4]  -> append  [4]
                    [4] , [5]  -> discard [5]

        result    : [0] , [2] , [4]
    """
    def load_chatdata(filename):
        return parser.parse(
            json.loads(_open_file(
                "tests/testdata/extract_duplcheck/head/" + filename))
        )[1]
    # chat data offsets are ignored.
    blocks = (
        Block(first=0, last=2500, chat_data=load_chatdata("dp0-0.json")),
        Block(first=1500, last=2500, chat_data=load_chatdata("dp0-1.json")),
        Block(first=10000, last=45146, chat_data=load_chatdata("dp0-2.json")),
        Block(first=20244, last=45146, chat_data=load_chatdata("dp0-3.json")),
        Block(first=20244, last=62875, chat_data=load_chatdata("dp0-4.json")),
        Block(first=52568, last=62875, chat_data=load_chatdata("dp0-5.json"))
    )

    result = duplcheck.remove_duplicate_tail(blocks)
    _dump(result)
    assert len(result) == 3
    assert result[0].first == blocks[0].first
    assert result[0].last == blocks[0].last
    assert result[1].first == blocks[2].first
    assert result[1].last == blocks[2].last
    assert result[2].first == blocks[4].first
    assert result[2].last == blocks[4].last
