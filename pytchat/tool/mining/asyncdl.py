
import aiohttp
import asyncio
import json
from . import parser
from . block import Block
from . dlworker import DownloadWorker
from . patch import Patch
from ... import config 
from ... paramgen import arcparam_mining as arcparam
from concurrent.futures import CancelledError
from urllib.parse import quote

headers = config.headers
REPLAY_URL = "https://www.youtube.com/live_chat_replay?continuation="
INTERVAL = 1
def _split(start, end, count, min_interval_sec = 120):
    """
    Split section from `start` to `end` into `count` pieces,
    and returns the beginning of each piece. 
    The `count` is adjusted so that the length of each piece
    is no smaller than `min_interval`.

    Returns:
    --------
        List of the offset of each block's first chat data.
    """
    
    if not (isinstance(start,int) or isinstance(start,float)) or \
       not (isinstance(end,int) or isinstance(end,float)):
        raise ValueError("start/end must be int or float")
    if not isinstance(count,int):
        raise ValueError("count must be int")
    if start>end:
        raise ValueError("end must be equal to or greater than start.")
    if count<1:
        raise ValueError("count must be equal to or greater than 1.")
    if (end-start)/count < min_interval_sec:
        count = int((end-start)/min_interval_sec) 
        if count == 0 : count = 1
    interval= (end-start)/count 
    
    if count == 1:
        return [start]
    return sorted( list(set( [int(start + interval*j)
        for j in range(count) ])))

def ready_blocks(video_id, duration, div, callback):
    if div <= 0: raise ValueError

    async def _get_blocks( video_id, duration, div, callback):
        async with aiohttp.ClientSession() as session:
            tasks = [_create_block(session, video_id,  seektime, callback)
                for  seektime in _split(0, duration, div)]
            return await asyncio.gather(*tasks)

    

    async def _create_block(session, video_id, seektime, callback):
        continuation = arcparam.getparam(video_id, seektime = seektime)
        url=(f"{REPLAY_URL}{quote(continuation)}&playerOffsetMs="
            f"{int(seektime*1000)}&hidden=false&pbj=1")
        async with session.get(url, headers = headers) as resp:
            chat_json = await resp.text()
        if chat_json is None:
            return
        continuation, actions = parser.parse(json.loads(chat_json)[1])
        first = seektime
        seektime += INTERVAL
        if callback:
            callback(actions, INTERVAL)
        return Block(
            continuation = continuation,
            chat_data = actions,
            first = first,
            last = seektime,
            seektime = seektime
        )
    """
    fetch initial blocks.
    """  
    loop = asyncio.get_event_loop()
    blocks = loop.run_until_complete(
        _get_blocks(video_id, duration, div, callback))
    return blocks

def download_patch(callback, blocks, video_id):

    async def _allocate_workers():
        workers = [
            DownloadWorker(
                fetch = _fetch,  block = block,
                blocks = blocks, video_id = video_id
            )
            for block in blocks
        ]
        async with aiohttp.ClientSession() as session:
            tasks = [worker.run(session) for worker in workers]
            return await asyncio.gather(*tasks)    

    async def _fetch(seektime,session) -> Patch:
        continuation = arcparam.getparam(video_id, seektime = seektime)
        url=(f"{REPLAY_URL}{quote(continuation)}&playerOffsetMs="
            f"{int(seektime*1000)}&hidden=false&pbj=1")
        async with session.get(url,headers = config.headers) as resp:
            chat_json = await resp.text()
        actions = []
        try:
            if chat_json is None:
                return Patch()
            continuation, actions = parser.parse(json.loads(chat_json)[1])
        except json.JSONDecodeError:
            pass
        if callback:
            callback(actions, INTERVAL)
        return Patch(chats = actions, continuation = continuation, 
            seektime = seektime, last = seektime)
    """
    allocate workers and assign blocks.
    """   
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_allocate_workers())
    except CancelledError:
        pass

async def _shutdown():
    print("\nshutdown...")
    tasks = [t for t in asyncio.all_tasks()
         if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

def cancel():
    loop = asyncio.get_event_loop()
    loop.create_task(_shutdown())
    