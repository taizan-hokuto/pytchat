import aiohttp
import asyncio
import json
from pytchat.tool import parser
import sys
import time
from aioresponses import aioresponses
from concurrent.futures import CancelledError
from pytchat.tool import asyncdl

def _open_file(path):
    with open(path,mode ='r',encoding = 'utf-8') as f:
        return f.read()


def test_asyncdl_split(mocker):

    ret = asyncdl._split(0,1000,1)
    assert ret == [0]

    ret = asyncdl._split(1000,1000,10)
    assert ret == [1000]

    ret = asyncdl._split(0,1000,5)
    assert ret == [0,200,400,600,800]

    ret = asyncdl._split(10.5, 700.3, 5)
    assert ret == [10, 148, 286, 424, 562]


    ret = asyncdl._split(0,500,5)
    assert ret == [0,125,250,375]
    
    ret = asyncdl._split(0,500,500)
    assert ret == [0,125,250,375]
    
    ret = asyncdl._split(-1,1000,5)
    assert ret == [-1, 199, 399, 599, 799]
    
    """invalid argument order"""
    try:
        ret = asyncdl._split(500,0,5)
        assert False
    except ValueError:
        assert True

    """invalid count"""
    try:
        ret = asyncdl._split(0,500,-1)
        assert False
    except ValueError:
        assert True

    try:
        ret = asyncdl._split(0,500,0)
        assert False
    except ValueError:
        assert True

    """invalid argument type"""
    try:
        ret = asyncdl._split(0,5000,5.2)
        assert False
    except ValueError:
        assert True

    try:
        ret = asyncdl._split(0,5000,"test")
        assert False
    except ValueError:
        assert True

    try:
        ret = asyncdl._split([0,1],5000,5)
        assert False
    except ValueError:
        assert True