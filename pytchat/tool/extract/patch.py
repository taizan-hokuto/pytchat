from . import parser
from . block import Block
from typing import NamedTuple


class Patch(NamedTuple):
    """
    Patch represents chunk of chat data
    which is fetched by asyncdl.fetch_patch._fetch().
    """
    chats: list = []
    continuation: str = None
    first: int = None
    last: int = None


def fill(block: Block, patch: Patch):
    block_end = block.end
    if patch.last < block_end or block.is_last:
        set_patch(block, patch)
        return
    for line in reversed(patch.chats):
        line_offset = parser.get_offset(line)
        if line_offset < block_end:
            break
        patch.chats.pop()
    set_patch(block, patch._replace(
        continuation=None,
        last=line_offset
    )
    )
    block.remaining = 0
    block.done = True


def split(parent_block: Block, child_block: Block, patch: Patch):
    parent_block.during_split = False
    if patch.first <= parent_block.last:
        ''' When patch overlaps with parent_block,
        discard this block. '''
        child_block.continuation = None
        ''' Leave child_block.during_split == True
         to exclude from during_split sequence. '''
        return
    child_block.during_split = False
    child_block.first = patch.first
    parent_block.end = patch.first
    fill(child_block, patch)


def set_patch(block: Block, patch: Patch):
    block.continuation = patch.continuation
    block.chat_data.extend(patch.chats)
    block.last = patch.last
    block.remaining = block.end - block.last
