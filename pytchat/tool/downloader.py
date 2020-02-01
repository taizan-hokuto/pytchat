import asyncio
import aiohttp
import json
import traceback
from urllib.parse import quote
from . import parser
from . import videoinfo
from . dlworker import DownloadWorker
from . duplcheck import duplicate_head, duplicate_tail, overwrap
from .. import config
from .. import util
from .. paramgen import arcparam
from ..exceptions import InvalidVideoIdException

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
        self.blocks = duplicate_head(self.blocks)
        return self

    def set_temporary_last(self):
        for i in range(len(self.blocks)-1):
            self.blocks[i].temp_last = self.blocks[i+1].first
        self.blocks[-1].temp_last = -1
        return self

    def remove_overwrap(self):
        self.blocks = overwrap(self.blocks)
        return self

    def download_blocks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._dl_distribute())
        return self

    async def _dl_distribute(self):
        workers = [
            DownloadWorker(
                dl=self.dl_func,
                block = block,
                blocklist= self.blocks
            )
            for pos,block in enumerate(self.blocks)
        ]
        async with aiohttp.ClientSession() as session:
            tasks = [worker.run(session) for worker in workers]
            return await asyncio.gather(*tasks,return_exceptions=True)    

    async def dl_func(self,continuation,session):
        url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
        async with session.get(url,headers = config.headers) as resp:
            text = await resp.text()
        continuation, actions = parser.parse(json.loads(text))
        if actions:
            last = parser.get_offset(actions[-1])
            first = parser.get_offset(actions[0])
            if self.callback:
                self.callback(actions,last-first)
            return actions,continuation,last
        return continuation, [], None
    
    def remove_duplicate_tail(self):
        self.blocks = duplicate_tail(self.blocks)
        return self

    def combine(self):
        ret = []
        for block in self.blocks:
            ret.extend(block.chat_data) 
        return ret

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
    

def download(video_id, div = 20, callback=None, processor = None):
    duration = 0
    try:
        duration = videoinfo(video_id).get("duration")
    except InvalidVideoIdException:
        raise
    if duration == 0:
        print("video is live.")
        return 
    return Downloader(video_id, duration, div, callback).download()