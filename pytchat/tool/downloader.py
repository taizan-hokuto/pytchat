import asyncio
import aiohttp
import json
import traceback
from urllib.parse import quote

from . import parser
from .. import config
from .. import util
from .. paramgen import arcparam

logger = config.logger(__name__)
headers=config.headers

REPLAY_URL = "https://www.youtube.com/live_chat_replay/" \
             "get_live_chat_replay?continuation="
class Block:
    def __init__(self, pos=0, first=0, last=0,
                continuation='', chat_data=[]):
        self.pos = pos
        self.first = first
        self.last = last
        self.temp_last = 0
        self.continuation = continuation
        self.chat_data = chat_data

class Downloader:
    def __init__(self, video_id, duration, div, callback=None):
        self.video_id = video_id
        self.duration = duration
        self.div = div
        self.blocks = []
        self.callback = callback


    def ready_blocks(self):
        if self.div <= 0: raise ValueError

        def _divide(start, end, count):
            min_interval = 120
            if (not isinstance(start,int) or 
                not isinstance(end,int) or 
                not isinstance(count,int)):
                raise ValueError("start/end/count must be int")
            if start>end:
                raise ValueError("end must be equal to or greater than start.")
            if count<1:
                raise ValueError("count must be equal to or greater than 1.")
            if (end-start)/count < min_interval:
                count = int((end-start)/min_interval) 
                if count == 0 : count = 1
            interval= (end-start)/count 
            
            if count == 1:
                return [start]
            return sorted(list(set([int(start+interval*j)
                for j in range(count) ])))

        async def _get_blocks(duration,div):
            async with aiohttp.ClientSession() as session:
                futures = [_create_block(session, pos, seektime)
                    for pos, seektime in enumerate(_divide(-1, duration, div))]
                return await asyncio.gather(*futures,return_exceptions=True)

        async def _create_block(session, pos, seektime):
            continuation = arcparam.getparam(
                self.video_id, seektime = seektime)
            
            url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
            async with session.get(url, headers = headers) as resp:
                text = await resp.text()
            next_continuation, actions = parser.parse(json.loads(text))
            if actions:
                first = parser.get_offset(actions[0])
                last = parser.get_offset(actions[-1])
                if self.callback:
                    self.callback(actions,last-first)
                return Block(
                    pos = pos,
                    continuation = next_continuation,
                    chat_data = actions,
                    first = first,
                    last = last
                )

        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            _get_blocks(self.duration, self.div))
        self.blocks = [block for block in result if block]
        return self  

    def remove_duplicate_head(self):
        blocks = self.blocks

        def is_same_offset(index):
            return (blocks[index].first == blocks[index+1].first)

        def is_same_id(index):
            id_0 = parser.get_id(blocks[index].chat_data[0])
            id_1 = parser.get_id(blocks[index+1].chat_data[0])
            return (id_0 == id_1)

        def is_same_type(index):
            type_0 = parser.get_type(blocks[index].chat_data[0])
            type_1 = parser.get_type(blocks[index+1].chat_data[0])
            return (type_0 == type_1)

        ret = []
        [ret.append(blocks[i]) for i in range(len(blocks)-1)
            if (len(blocks[i].chat_data)>0 and 
            not ( is_same_offset(i) and is_same_id(i) and is_same_type(i)))]
        ret.append(blocks[-1])
        self.blocks = ret
        return self

    def set_temporary_last(self):
        for i in range(len(self.blocks)-1):
            self.blocks[i].temp_last = self.blocks[i+1].first
        self.blocks[-1].temp_last = -1
        return self

    def remove_overwrap(self):
        blocks = self.blocks
        if len(blocks) == 1 : return self

        ret = []
        a = 0
        b = 1
        jmp = False
        ret.append(blocks[0])
        while a < len(blocks)-2:
            while blocks[a].last > blocks[b].first:
                b+=1
                if b == len(blocks)-1:
                    jmp = True    
                    break
            if jmp: break
            if b-a == 1:
                a = b
            else:
                a = b-1
            ret.append(blocks[a])
            b = a+1

        ret.append(blocks[-1])
        self.blocks = ret
        return self

    def download_blocks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._dl_allocate())
        return self

    async def _dl_allocate(self):
        tasks = []
        async with aiohttp.ClientSession() as session:
            tasks = [self._dl_task(session, block) for block in self.blocks]
            return await asyncio.gather(*tasks,return_exceptions=True)    

    async def _dl_task(self, session, block:Block):
        if (block.temp_last != -1 and
            block.last > block.temp_last):
            return 

        def get_last_offset(actions):
            return parser.get_offset(actions[-1])

        continuation = block.continuation
        while continuation:
            url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
            async with session.get(url,headers = config.headers) as resp:
                text = await resp.text()
            continuation, actions = parser.parse(json.loads(text))
            if actions:
                block.chat_data.extend(actions)
                last = get_last_offset(actions)
                first = parser.get_offset(actions[0])
                if self.callback:
                    self.callback(actions,last-first)
                if block.temp_last != -1:
                    if last > block.temp_last:
                        block.last = last
                        break
                else:
                    block.last = last

    def remove_duplicate_tail(self):
        blocks = self.blocks
        if len(blocks) == 1 : return self

        def is_same_offset(index):
            return (blocks[index-1].last == blocks[index].last)

        def is_same_id(index):
            id_0 = parser.get_id(blocks[index-1].chat_data[-1])
            id_1 = parser.get_id(blocks[index].chat_data[-1])
            return (id_0 == id_1)

        def is_same_type(index):
            type_0 = parser.get_type(blocks[index-1].chat_data[-1])
            type_1 = parser.get_type(blocks[index].chat_data[-1])
            return (type_0 == type_1)

        ret = []
        ret.append(blocks[0])
        [ret.append(blocks[i]) for i in range(1,len(blocks)-1)
            if not ( is_same_offset(i) and is_same_id(i) and is_same_type(i) )]
        ret.append(self.blocks[-1])
        self.blocks = ret
        return self

    def combine(self):
        line = ''
        try:
            if len(self.blocks[0].chat_data)>0:
                lastline=self.blocks[0].chat_data[-1]
                lastline_offset = parser.get_offset(lastline)
            else: return None
            for i in range(1,len(self.blocks)):
                f=self.blocks[i].chat_data
                if len(f)==0:
                    logger.error(f'zero size piece.:{str(i)}')
                    continue
                for row in range(len(f)):
                    line = f[row]
                    if parser.get_offset(line) > lastline_offset:
                        self.blocks[0].chat_data.extend(f[row:])
                        break
                else:
                    logger.error(
                        f'Missing connection.: pos:{str(i-1)}->{str(i)}'
                        f' lastline_offset= {lastline_offset}')
                lastline_offset = parser.get_offset( f[-1])
            return self.blocks[0].chat_data
        except Exception as e:
            logger.error(f"{type(e)} {str(e)} {line}")
            traceback.print_exc()
            

    def download(self):
        return (
            self.ready_blocks()
                .remove_duplicate_head()
                .set_temporary_last()
                .remove_overwrap()
                .download_blocks()
                .remove_duplicate_tail()
                .combine()
        )
    
def check_duplicate(blocks):
    
    def is_same_offset(index):
        offset_0 = parser.get_offset(blocks[index])
        offset_1 = parser.get_offset(blocks[index+1])
        return (offset_0 == offset_1)

    def is_same_id(index):
        id_0 = parser.get_id(blocks[index])
        id_1 = parser.get_id(blocks[index+1])
        return (id_0 == id_1)

    def is_same_type(index):
        type_0 = parser.get_type(blocks[index])
        type_1 = parser.get_type(blocks[index+1])
        return (type_0 == type_1)
    ret =[]
    for i in range(len(blocks)-1):
        if  ( is_same_offset(i) and is_same_id(i) and is_same_type(i) ):
            ret.append(blocks[i])
    return ret