import asyncio
import httpx
import socket
from concurrent.futures import CancelledError
from json import JSONDecodeError
from . import parser
from . block import Block
from . worker import ExtractWorker
from . patch import Patch
from ... import config
from ... paramgen import arcparam
from ... exceptions import UnknownConnectionError
from ... util import get_param


headers = config.headers
smr = config._smr

MAX_RETRY_COUNT = 3

# Set to avoid duplicate parameters
aquired_params = set()
dat = ''


def _split(start, end, count, min_interval_sec=120):
    """
    Split section from `start` to `end` into `count` pieces,
    and returns the beginning of each piece.
    The `count` is adjusted so that the length of each piece
    is no smaller than `min_interval`.

    Returns:
    --------
        List of the offset of each block's first chat data.
    """
    if not (isinstance(start, int) or isinstance(start, float)) or \
       not (isinstance(end, int) or isinstance(end, float)):
        raise ValueError("start/end must be int or float")
    if not isinstance(count, int):
        raise ValueError("count must be int")
    if start > end:
        raise ValueError("end must be equal to or greater than start.")
    if count < 1:
        raise ValueError("count must be equal to or greater than 1.")
    if (end - start) / count < min_interval_sec:
        count = int((end - start) / min_interval_sec)
        if count == 0:
            count = 1
    interval = (end - start) / count

    if count == 1:
        return [start]
    return sorted(list(set([int(start + interval * j)
                            for j in range(count)])))


def ready_blocks(video_id, duration, div, callback):
    aquired_params.clear()
    if div <= 0:
        raise ValueError

    async def _get_blocks(video_id, duration, div, callback):
        async with httpx.AsyncClient(http2=True, headers=headers) as session:
            tasks = [_create_block(session, video_id, seektime, callback)
                     for seektime in _split(-1, duration, div)]
            return await asyncio.gather(*tasks)

    async def _create_block(session, video_id, seektime, callback):
        continuation = arcparam.getparam(video_id, seektime=seektime)
        err = None
        last_offset = 0
        global dat
        for _ in range(MAX_RETRY_COUNT):
            try:
                if continuation in aquired_params:
                    next_continuation, actions = None, []
                    break
                aquired_params.add(continuation)
                param = get_param(continuation, replay=True, offsetms=seektime * 1000, dat=dat)
                resp = await session.post(smr, json=param, timeout=10)
                next_continuation, actions, last_offset, dat = parser.parse(resp.json())
                break
            except JSONDecodeError:
                await asyncio.sleep(3)
            except httpx.HTTPError as e:
                err = e
                await asyncio.sleep(3)
        else:
            cancel()
            raise UnknownConnectionError("Abort:" + str(err))

        if actions:
            first_offset = parser.get_offset(actions[0])
            if callback:
                callback(actions, last_offset - first_offset)
            return Block(
                continuation=next_continuation,
                chat_data=actions,
                first=first_offset,
                last=last_offset
            )

    """
    fetch initial blocks.
    """
    loop = asyncio.get_event_loop()
    blocks = loop.run_until_complete(
        _get_blocks(video_id, duration, div, callback))
    return blocks


def fetch_patch(callback, blocks, video_id):

    async def _allocate_workers():
        workers = [
            ExtractWorker(
                fetch=_fetch, block=block,
                blocks=blocks, video_id=video_id
            )
            for block in blocks
        ]
        async with httpx.AsyncClient() as session:
            tasks = [worker.run(session) for worker in workers]
            return await asyncio.gather(*tasks)

    async def _fetch(continuation, last_offset, session=None) -> Patch:
        global dat
        err = None
        for _ in range(MAX_RETRY_COUNT):
            try:
                if continuation in aquired_params:
                    continuation, actions = None, []
                    break
                aquired_params.add(continuation)
                params = get_param(continuation, replay=True, offsetms=last_offset, dat=dat)
                # util.save(json.dumps(params, ensure_ascii=False), "v:/~~/param_"+str(last_offset), ".json")
                resp = await session.post(smr, json=params)
                continuation, actions, last_offset, dat = parser.parse(resp.json())
                break
            except JSONDecodeError:
                await asyncio.sleep(3)
            except httpx.HTTPError as e:
                err = e
                await asyncio.sleep(3)
            except socket.error as error:
                print("socket error", error.errno)
                await asyncio.sleep(3)
        else:
            cancel()
            raise UnknownConnectionError("Abort:" + str(err))

        if actions:
            last = last_offset
            first = parser.get_offset(actions[0])
            if callback:
                callback(actions, last - first)
            return Patch(actions, continuation, first, last)
        return Patch(continuation=continuation)

    """
    allocate workers and assign blocks.
    """
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_allocate_workers())
    except CancelledError:
        pass


async def _shutdown():
    tasks = [t for t in asyncio.all_tasks()
             if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()


def cancel():
    loop = asyncio.get_event_loop()
    loop.create_task(_shutdown())
