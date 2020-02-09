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

def load_chatdata(filename):
        return parser.parse(
            json.loads(_open_file("tests/testdata/dl_duplcheck/head/"+filename))
        )[1]

def test_overwrap(mocker):
    """
    test overwrap data 
        operation : [0] , [1] -> discard [1]
                    [0] , [2] , [3] -> discard [2]
                    [3] , [4] , [5] -> discard [4]
        result    : [0] , [3] , [5] 

    """
    blocks = (
        Block(first = 0,last= 38771, chat_data = load_chatdata("dp0-0.json")),     
        Block(first = 9890,last= 38771, chat_data = load_chatdata("dp0-1.json")), 
        Block(first = 20244,last= 45146, chat_data = load_chatdata("dp0-2.json")), 
        Block(first = 32476,last= 60520, chat_data = load_chatdata("dp0-3.json")), 
        Block(first = 41380,last= 62875, chat_data = load_chatdata("dp0-4.json")), 
        Block(first = 52568,last= 62875, chat_data = load_chatdata("dp0-5.json"))
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


    blocks = (
        Block(first = 0, last = 2500, chat_data = load_chatdata("dp0-0.json")),     
        Block(first = 0, last =38771, chat_data = load_chatdata("dp0-1.json")), 
        Block(first = 0, last =45146, chat_data = load_chatdata("dp0-2.json")), 
        Block(first = 20244, last =60520, chat_data = load_chatdata("dp0-3.json")), 
        Block(first = 20244, last =62875, chat_data = load_chatdata("dp0-4.json")), 
        Block(first = 52568, last =62875, chat_data = load_chatdata("dp0-5.json"))
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

    blocks = (
        Block(first = 0,last = 2500, chat_data=load_chatdata("dp0-0.json")),     
        Block(first = 1500,last = 2500, chat_data=load_chatdata("dp0-1.json")), 
        Block(first = 10000,last = 45146, chat_data=load_chatdata("dp0-2.json")), 
        Block(first = 20244,last = 45146, chat_data=load_chatdata("dp0-3.json")), 
        Block(first = 20244,last = 62875, chat_data=load_chatdata("dp0-4.json")), 
        Block(first = 52568,last = 62875, chat_data=load_chatdata("dp0-5.json"))
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


