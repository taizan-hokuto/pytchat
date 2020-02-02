
import aiohttp
import asyncio
import json
from . import parser
from . block import Block
from . dlworker import DownloadWorker
from .. paramgen import arcparam
from .. import config 
from urllib.parse import quote

headers = config.headers
REPLAY_URL = "https://www.youtube.com/live_chat_replay/" \
             "get_live_chat_replay?continuation="

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

def ready_blocks(video_id, duration, div, callback):
    if div <= 0: raise ValueError

    async def _get_blocks( video_id, duration, div, callback):
        async with aiohttp.ClientSession() as session:
            futures = [_create_block(session, video_id, pos, seektime, callback)
                for pos, seektime in enumerate(_divide(-1, duration, div))]
            return await asyncio.gather(*futures,return_exceptions=True)

    async def _create_block(session, video_id, pos, seektime, callback):
        continuation = arcparam.getparam(
            video_id, seektime = seektime)
        
        url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
        async with session.get(url, headers = headers) as resp:
            text = await resp.text()
        next_continuation, actions = parser.parse(json.loads(text))
        if actions:
            first = parser.get_offset(actions[0])
            last = parser.get_offset(actions[-1])
            if callback:
                callback(actions,last-first)
            return Block(
                pos = pos,
                continuation = next_continuation,
                chat_data = actions,
                first = first,
                last = last
            )

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        _get_blocks(video_id, duration, div, callback))
    return result

def download_chunk(callback, blocks):

    async def _allocate_workers():
        workers = [
            DownloadWorker(
                fetch = _fetch,
                block = block
            )
            for block in blocks
        ]
        async with aiohttp.ClientSession() as session:
            tasks = [worker.run(session) for worker in workers]
            return await asyncio.gather(*tasks,return_exceptions=True)    

    async def _fetch(continuation,session):
        url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
        async with session.get(url,headers = config.headers) as resp:
            chat_json = await resp.text()
        continuation, actions = parser.parse(json.loads(chat_json))
        if actions:
            last = parser.get_offset(actions[-1])
            first = parser.get_offset(actions[0])
            if callback:
                callback(actions, last - first)
            return actions, continuation, last
        return continuation, [], None
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_allocate_workers())
