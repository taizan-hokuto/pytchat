
import aiohttp
import asyncio
import json
from . import parser
from . block import Block
from . dlworker import DownloadWorker
from .. paramgen import arcparam
from .. import config 
from urllib.parse import quote
from concurrent.futures import CancelledError

headers = config.headers
REPLAY_URL = "https://www.youtube.com/live_chat_replay/" \
             "get_live_chat_replay?continuation="

def _split(start, end, count, min_interval = 120):
    """
    Split section from `start` to `end` into `count` pieces,
    and returns the beginning of each piece. 
    The `count` is adjusted so that the length of each piece
    is no smaller than `min_interval`.

    Returns:
    --------
    List of the beginning position of each piece.
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
            tasks = [_create_block(session, video_id, pos, seektime, callback)
                for pos, seektime in enumerate(_split(-1, duration, div))]
            return await asyncio.gather(*tasks)

    async def _create_block(session, video_id, pos, seektime, callback):
        continuation = arcparam.getparam(
            video_id, seektime = seektime)
        
        url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
        for _ in range(3):
            try:
                async with session.get(url, headers = headers) as resp:
                    text = await resp.text()
                next_continuation, actions = parser.parse(json.loads(text))
            except json.JSONDecodeError:
                print("JSONDecodeError occured")
                await asyncio.sleep(1)
                continue
            break
        else:
            raise json.JSONDecodeError
        if actions:
            first = parser.get_offset(actions[0])
            last = parser.get_offset(actions[-1])
            if callback:
                callback(actions,last-first)
            return Block(
                continuation = next_continuation,
                chat_data = actions,
                first = first,
                last = last
            )

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        _get_blocks(video_id, duration, div, callback))
    return result

def download_chunk(callback, blocks, video_id):

    async def _allocate_workers():
        workers = [
            DownloadWorker(
                fetch = _fetch,
                block = block,
                blocks = blocks,
                video_id = video_id

            )
            for i,block in enumerate(blocks)
        ]
        async with aiohttp.ClientSession() as session:
            tasks = [worker.run(session) for worker in workers]
            return await asyncio.gather(*tasks)    

    async def _fetch(continuation,session):
        url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
        for _ in range(3):
            try:
                async with session.get(url,headers = config.headers) as resp:
                    chat_json = await resp.text()
            except json.JSONDecodeError:
                print("JSONDecodeError occured")
                await asyncio.sleep(1)
                continue
            break
        else:
            raise json.JSONDecodeError
        continuation, actions = parser.parse(json.loads(chat_json))
        if actions:
            last = parser.get_offset(actions[-1])
            first = parser.get_offset(actions[0])
            if callback:
                callback(actions, last - first)
            return actions, continuation, first, last
        return [], continuation, None, None
    
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_allocate_workers())
    except CancelledError:
        pass


async def shutdown():
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
    loop.create_task(shutdown())
    