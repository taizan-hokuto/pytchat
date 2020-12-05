from . block import Block
from . patch import fill, split
from ... paramgen import arcparam
from typing import Tuple


class ExtractWorker:
    """
    ExtractWorker associates a download session with a block.
    When the worker finishes fetching, the block
    being fetched is splitted and assigned the free worker.

    Parameter
    ----------
    fetch : func :
        extract function of asyncdl

    block : Block :
        Block object that includes chat_data

    blocks : list :
        List of Block(s)

    video_id : str :

    parent_block : Block :
        the block from which current block is splitted
    """
    __slots__ = ['block', 'fetch', 'blocks', 'video_id', 'parent_block']

    def __init__(self, fetch, block, blocks, video_id):
        self.block = block
        self.fetch = fetch
        self.blocks = blocks
        self.video_id = video_id
        self.parent_block = None

    async def run(self, session):
        while self.block.continuation:
            patch = await self.fetch(
                self.block.continuation, self.block.last, session)
            if patch.continuation is None:
                """TODO : make the worker assigned to the last block
                to work more than twice as possible.
                """
                break
            if self.parent_block:
                split(self.parent_block, self.block, patch)
                self.parent_block = None
            else:
                fill(self.block, patch)
            if self.block.continuation is None:
                """finished fetching this block """
                self.block.done = True
                self.block = _search_new_block(self)


def _search_new_block(worker) -> Block:
    index, undone_block = _get_undone_block(worker.blocks)
    if undone_block is None:
        return Block(continuation=None)
    mean = (undone_block.last + undone_block.end) / 2
    continuation = arcparam.getparam(worker.video_id, seektime=mean / 1000)
    worker.parent_block = undone_block
    worker.parent_block.during_split = True
    new_block = Block(
        end=undone_block.end,
        chat_data=[],
        continuation=continuation,
        during_split=True,
        is_last=worker.parent_block.is_last)
    '''swap last block'''
    if worker.parent_block.is_last:
        worker.parent_block.is_last = False
    worker.blocks.insert(index + 1, new_block)
    return new_block


def _get_undone_block(blocks) -> Tuple[int, Block]:
    min_interval_ms = 120000
    max_remaining = 0
    undone_block = None
    index_undone_block = 0
    for index, block in enumerate(blocks):
        if block.done or block.during_split:
            continue
        remaining = block.remaining
        if remaining > max_remaining and remaining > min_interval_ms:
            index_undone_block = index
            undone_block = block
            max_remaining = remaining
    return index_undone_block, undone_block
