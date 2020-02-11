from . import parser
from .. paramgen import arcparam
from . block import Block
class DownloadWorker:
    """
    DownloadWorker associates a download session with a block.

    Parameter
    ----------
    fetch : func :
        download function of asyncdl

    block : Block :
        Block object associated with this worker 
    
    blocks : list :
        List of Block(s)

    video_id : str :

    source_block : Block :
        the Block from which current downloading block is splitted 
    """
    __slots__ = ['fetch', 'block', 'blocks', 'video_id', 'source_block']

    def __init__(self, fetch, block, blocks, video_id ):
        self.block = block
        self.fetch = fetch
        self.blocks = blocks
        self.video_id = video_id
        self.source_block = None

    async def run(self, session):
        """Remove extra chats just after ready_blocks(). """
        continuation = initial_fill(self.block)
        """download loop """
        while continuation:
            chats, new_cont, fetched_first, fetched_last = await self.fetch(
                continuation, session)
            if fetched_first is None:
                break
            if self.source_block:
                continuation = split_fill(
                    self.source_block, self.block, chats, new_cont, 
                    fetched_first, fetched_last)
                self.source_block = None
            else:    
                continuation = fill(self.block, chats, new_cont, fetched_last)

            if continuation is None:
                new_block = get_new_block(self)
                self.block = new_block
                continuation = new_block.continuation

def get_new_block(worker) -> Block:
    worker.block.done = True
    index,undone_block = search_undone_block(worker.blocks)
    if undone_block is None:
        return Block(continuation = None)
    mean = (undone_block.end + undone_block.last)/2
    continuation = arcparam.getparam(worker.video_id, seektime = mean/1000)
    worker.source_block = undone_block
    worker.source_block.splitting = True
    new_block = Block(
        end =  undone_block.end,
        chat_data = [], 
        continuation = continuation,
        splitting = True,
        is_last = worker.source_block.is_last)
    worker.blocks.insert(index+1,new_block)
    return new_block

def search_undone_block(blocks) -> (int, Block):
    """
    Returns 
    --------
    ret_index : int :
        index of Block download not completed in blocks .
    
    ret_block : Block :
        Block download not completed.
    """
    max_remaining = 0
    ret_block = None
    ret_index = 0
    for index, block in enumerate(blocks):
        if block.done or block.splitting:
            continue
        remaining = block.remaining
        if remaining > max_remaining and remaining > 120000:
            ret_index = index
            ret_block = block
            max_remaining = remaining
    return ret_index, ret_block

def top_cut(chats, last) -> list:
    for i, chat in enumerate(chats):
        if parser.get_offset(chat) > last:
            return chats[i:]
    return []

def bottom_cut(chats, last) -> list:
    for rchat in reversed(chats):
        if parser.get_offset(rchat)>=last:
            chats.pop()
        else:
            break
    return chats
            
def split_fill(source_block, block,  chats, new_cont, 
    fetched_first, fetched_last):
    if fetched_last <= source_block.last:
        return None
    block.splitting = False
    source_block.splitting = False
    source_block.end =  fetched_first
    block.first = fetched_first
    block.last = fetched_last
    continuation = new_cont
    if fetched_first < source_block.last:
        chats = top_cut(chats, source_block.last)
        block.first = source_block.last
    if block.end < fetched_last:
        chats = bottom_cut(chats, block.end)
        block.last = block.end
        continuation = None
    block.chat_data.extend(chats)
    block.continuation = continuation
    return continuation

def initial_fill(block):
    chats, cont = get_chats(block, block.chat_data, block.continuation, block.last)
    block.chat_data = chats
    return cont

def fill(block, chats, cont, fetched_last):
    chats, cont = get_chats(block, chats, cont, fetched_last)
    block.chat_data.extend(chats)
    return cont

def get_chats(block, chats, cont, fetched_last):
    block.last = fetched_last
    if fetched_last < block.end or block.is_last:
        block.last = fetched_last
        block.remaining=block.end-block.last
        return chats, cont
    for i, line in enumerate(chats):
        line_offset = parser.get_offset(line)
        if line_offset >= block.end:
            block.last = line_offset
            block.remaining = 0
            block.done = True
            return chats[:i], None