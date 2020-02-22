from . import parser
from . block import Block
from typing import NamedTuple

class Patch(NamedTuple):
    """
    Patch represents chunk of chat data
    which is fetched by asyncdl.download_patch._fetch().
    """
    chats : list = []
    continuation : str = None
    seektime : float = None
    first : int = None
    last : int = None

def fill(block:Block, patch:Patch):
    if patch.last < block.end:
        set_patch(block, patch)
        return
    block.continuation = None

def set_patch(block:Block, patch:Patch):
    block.continuation = patch.continuation
    block.chat_data.extend(patch.chats)
    block.last = patch.seektime
    block.seektime = patch.seektime       

