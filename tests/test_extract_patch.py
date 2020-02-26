import aiohttp
import asyncio
import json
import os, sys
import time
from aioresponses import aioresponses
from pytchat.tool.extract import duplcheck
from pytchat.tool.extract import parser
from pytchat.tool.extract.block import Block
from pytchat.tool.extract.patch import Patch, fill, split, set_patch
from pytchat.tool.extract.duplcheck import _dump
def _open_file(path):
    with open(path,mode ='r',encoding = 'utf-8') as f:
        return f.read()

def load_chatdata(filename):
        return parser.parse(
            json.loads(_open_file("tests/testdata/fetch_patch/"+filename))
        )[1]


def test_split_0():
    """
    Normal case

    ~~~~~~ before ~~~~~~

     @parent_block  (# = already fetched)
    
     first    last                                     end
       |########----------------------------------------|
    

     @child_block
    
     first = last = 0                                  end (=parent_end)
       |                                                |
    

     @fetched patch
                            |-- patch --|
    
     
                            |
                            |
                            V 

    ~~~~~~ after ~~~~~~
    

     @parent_block
    
     first    last         end (after split)   
       |########------------|
    
     @child_block
                          first       last            end            
                            |###########---------------|
    
     @fetched patch
                            |-- patch --|
    """
    parent = Block(first=0, last=4000, end=60000, continuation='parent', during_split=True)
    child = Block(first=0, last=0, end=60000, continuation='mean', during_split=True)
    patch = Patch(chats=load_chatdata('pt0-5.json'),
        first=32500, last=34000, continuation='patch')
    
    split(parent,child,patch)

    assert child.continuation == 'patch'
    assert parent.last < child.first
    assert parent.end == child.first
    assert child.first < child.last
    assert child.last < child.end
    assert parent.during_split == False
    assert child.during_split == False

def test_split_1():
    """patch.first <= parent_block.last

    While awaiting at run()->asyncdl._fetch()
    fetching parent_block proceeds, 
    and parent.block.last exceeds patch.first.

    In this case, fetched patch is all discarded,
    and worker searches other processing block again. 

    ~~~~~~ before ~~~~~~

                          patch.first
      first                 |    last                  end
       |####################|#####|---------------------|
                            ^
     @child_block
     first = last = 0                                  end (=parent_end)
       |                                                |
     
     @fetched patch
                            |-- patch --|
    
     
                            |
                            |
                            V 
    
    ~~~~~~ after ~~~~~~

     @parent_block
     first                       last                  end
       |###########################|--------------------|
    
     @child_block
                                
                            ..............　-> 　discard all data
                   
    """
    parent = Block(first=0, last=33000, end=60000, continuation='parent', during_split=True)
    child = Block(first=0, last=0, end=60000, continuation='mean', during_split=True)
    patch = Patch(chats=load_chatdata('pt0-5.json'),
        first=32500, last=34000, continuation='patch')
    
    split(parent,child,patch)

    assert parent.last == 33000 #no change
    assert parent.end == 60000 #no change
    assert child.continuation is None
    assert parent.during_split == False
    assert child.during_split == True #exclude during_split sequence

def test_split_2():
    """child_block.end < patch.last:

    Case the last offset of patch exceeds child_block.end.
    In this case, remove overlapped data of patch.

    ~~~~~~ before ~~~~~~

     @parent_block  (# = already fetched)
     first    last                           end (before split)
       |########------------------------------|
    
     @child_block
     first = last = 0                        end (=parent_end)
       |                                      |
    
    continuation:succeed from patch
    
     @fetched patch
                            |-------- patch --------|
    
     
                            |
                            |
                            V 

    ~~~~~~ after ~~~~~~

     @parent_block
     first    last         end (after split)   
       |########------------|

     @child_block                                  old patch.end            
                          first            last=end |
                            |#################|......   cut extra data.
                                                    ^
    continuation : None (extract complete)

     @fetched patch                                 
                            |-------- patch --------|
    """
    parent = Block(first=0, last=4000, end=33500, continuation='parent', during_split=True)
    child = Block(first=0, last=0, end=33500, continuation='mean', during_split=True)
    patch = Patch(chats=load_chatdata('pt0-5.json'),
        first=32500, last=34000, continuation='patch')
     
    split(parent,child,patch)

    assert child.continuation is None
    assert parent.last < child.first
    assert parent.end == child.first
    assert child.first < child.last
    assert child.last < child.end
    assert child.continuation is None
    assert parent.during_split == False
    assert child.during_split == False

def test_split_none():
    """patch.last <= parent_block.last

    While awaiting at run()->asyncdl._fetch()
    fetching parent_block proceeds, 
    and parent.block.last exceeds patch.first.

    In this case, fetched patch is all discarded,
    and worker searches other processing block again. 
    
    ~~~~~~ before ~~~~~~

                          patch.first
     first                  |   last                   end
       |####################|###################|-------|
                            ^
     @child_block
     first = last = 0                                  end (=parent_end)
       |                                                |
     
     @fetched patch
                            |-- patch --|
                                      patch.last < parent_block.last                       .
     
                            |
                            |
                            V 
    
    ~~~~~~ after ~~~~~~

     @parent_block
     first                       last           end (before split)
       |########################################|-------|

     @child_block
                                           
                            ............    -> discard all data.

    """
    parent = Block(first=0, last=40000, end=60000, continuation='parent', during_split=True)
    child = Block(first=0, last=0, end=60000, continuation='mean', during_split=True)
    patch = Patch(chats=load_chatdata('pt0-5.json'),
        first=32500, last=34000, continuation='patch')
    
    split(parent,child,patch)

    assert parent.last == 40000 #no change
    assert parent.end == 60000 #no change
    assert child.continuation is None
    assert parent.during_split == False
    assert child.during_split == True #exclude during_split sequence
