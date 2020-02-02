import aiohttp
import asyncio
import json
import os, sys
import time
from aioresponses import aioresponses
from pytchat.tool import duplcheck
from pytchat.tool import parser
from pytchat.tool.block import Block
from pytchat.tool.duplcheck import _dump
def _open_file(path):
    with open(path,mode ='r',encoding = 'utf-8') as f:
        return f.read()

def test_overwrap(mocker):
    """
    test overwrap data 
        operation : [0] , [1] -> discard [1]
                    [0] , [2] , [3] -> discard [2]
                    [3] , [4] , [5] -> discard [4]
        result    : [0] , [3] , [5] 

    """
    blocks = (
        Block(0,     0, 38771, "",[]),     
        Block(1,  9890, 38771, "",[]), 
        Block(2, 20244, 45146, "",[]), 
        Block(3, 32476, 60520, "",[]), 
        Block(4, 41380, 62875, "",[]), 
        Block(5, 52568, 62875, "",[])
    )
    result = duplcheck.overwrap(blocks)
    assert len(result) == 3
    assert result[0].first == blocks[0].first
    assert result[0].last  == blocks[0].last
    assert result[1].first == blocks[3].first
    assert result[1].last  == blocks[3].last
    assert result[2].first == blocks[5].first
    assert result[2].last  == blocks[5].last
    
def test_duplicate_head(mocker):
    """
    test duplicate head data 
        operation : [0] , [1]  -> discard [0]
                    [1] , [2]  -> discard [1]
                    [2] , [3]  -> append [2]
                    [3] , [4]  -> discard [3]
                    [4] , [5]  -> append [4]
                    append [5]

        result    : [0] , [3] , [5] 
    """
    def load_chatdata(filename):
        return parser.parse(
            json.loads(_open_file("tests/testdata/dl_duplcheck/head/"+filename))
        )[1]

    blocks = (
        Block(0,     0,  2500, "",load_chatdata("dp0-0.json")),     
        Block(1,     0, 38771, "",load_chatdata("dp0-1.json")), 
        Block(2,     0, 45146, "",load_chatdata("dp0-2.json")), 
        Block(3, 20244, 60520, "",load_chatdata("dp0-3.json")), 
        Block(4, 20244, 62875, "",load_chatdata("dp0-4.json")), 
        Block(5, 52568, 62875, "",load_chatdata("dp0-5.json"))
    )
    _dump(blocks)
    result = duplcheck.duplicate_head(blocks)
    
    assert len(result) == 3
    assert result[0].first == blocks[2].first
    assert result[0].last  == blocks[2].last
    assert result[1].first == blocks[4].first
    assert result[1].last  == blocks[4].last
    assert result[2].first == blocks[5].first
    assert result[2].last  == blocks[5].last

def test_duplicate_tail(mocker):
    """
    test duplicate tail data 
        operation : append [0]
                    [0] , [1]  -> discard [1]
                    [1] , [2]  -> append [2]
                    [2] , [3]  -> discard [3]
                    [3] , [4]  -> append [4]
                    [4] , [5]  -> discard [5]

        result    : [0] , [2] , [4] 
    """
    def load_chatdata(filename):
        return parser.parse(
            json.loads(_open_file("tests/testdata/dl_duplcheck/head/"+filename))
        )[1]

    blocks = (
        Block(0,     0,  2500, "",load_chatdata("dp0-0.json")),     
        Block(1,  1500,  2500, "",load_chatdata("dp0-1.json")), 
        Block(2, 10000, 45146, "",load_chatdata("dp0-2.json")), 
        Block(3, 20244, 45146, "",load_chatdata("dp0-3.json")), 
        Block(4, 20244, 62875, "",load_chatdata("dp0-4.json")), 
        Block(5, 52568, 62875, "",load_chatdata("dp0-5.json"))
    )

    result = duplcheck.duplicate_tail(blocks)
    _dump(result)
    assert len(result) == 3
    assert result[0].first == blocks[0].first
    assert result[0].last  == blocks[0].last
    assert result[1].first == blocks[2].first
    assert result[1].last  == blocks[2].last
    assert result[2].first == blocks[4].first
    assert result[2].last  == blocks[4].last


