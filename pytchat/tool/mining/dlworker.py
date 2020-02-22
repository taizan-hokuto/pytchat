from . import parser
from . block import Block
from . patch import Patch, fill
from ... paramgen import arcparam
INTERVAL = 1
class DownloadWorker:
    """
    DownloadWorker associates a download session with a block.

    When the dlworker finishes downloading, the block
    being downloaded is splitted and assigned the free dlworker.

    Parameter
    ----------
    fetch : func :
        download function of asyncdl

    block : Block :
        Block object that includes chat_data
    
    blocks : list :
        List of Block(s)

    video_id : str :

    parent_block : Block :
        the block from which current block is splitted 
    """
    __slots__ = ['block', 'fetch', 'blocks', 'video_id', 'parent_block']
    def __init__(self, fetch, block, blocks, video_id ):
        self.block:Block = block
        self.fetch = fetch
        self.blocks:list = blocks
        self.video_id:str = video_id
        self.parent_block:Block = None


    async def run(self, session):
        while self.block.continuation:
            patch = await self.fetch(
                self.block.seektime, session)
            fill(self.block, patch)
            self.block.seektime += INTERVAL
        self.block.done = True    


def fd(name,mes,src,patch,end):
    def offset(chats):
        if len(chats)==0:
            return None,None
        return parser.get_offset(chats[0]),parser.get_offset(chats[-1])

    with open("v://tlog.csv",encoding="utf-8",mode="a") as f:
        f.write(f"WORKER,{name},mes,{mes},edge,{offset(src)[1]},first,{offset(patch)[0]},last,{offset(patch)[1]},end,{end}\n")
