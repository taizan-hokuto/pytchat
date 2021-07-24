import asyncio
import pytchat
from concurrent.futures import CancelledError
from pytchat.core_multithread.livechat import LiveChat
from pytchat.core_async.livechat import LiveChatAsync

cases = [
    {
        "video_id":"1X7oL0hDnMg", "seektime":1620,
        "result1":{'textMessage': 84},
        "result2":{'': 83, 'MODERATOR': 1}
    },
    {
        "video_id":"Hj-wnLIYKjw", "seektime":420,
        "result1":{'superChat': 1, 'newSponsor': 6, 'textMessage': 63, 'donation': 1},
        "result2":{'': 59, 'MEMBER': 12}
    },
    {
        "video_id":"S8dmq5YIUoc", "seektime":3,
        "result1":{'textMessage': 86},
        "result2":{'': 62, 'MEMBER': 21, 'OWNER': 2, 'VERIFIED': 1}
    },{
        "video_id":"yLrstz80MKs", "seektime":30,
        "result1":{'superSticker': 8, 'superChat': 2, 'textMessage': 67},
        "result2":{'': 73, 'MEMBER': 4}
    }
]

def test_archived_stream():
    for case in cases:
        stream = pytchat.create(video_id=case["video_id"], seektime=case["seektime"])
        while stream.is_alive():
            chat = stream.get()
            agg1 = {}
            agg2 = {}
            for c in chat.items:
                if c.type in agg1:
                    agg1[c.type] += 1
                else:
                    agg1[c.type] = 1
                if c.author.type in agg2:
                    agg2[c.author.type] += 1
                else:
                    agg2[c.author.type] = 1
            break
        assert agg1 == case["result1"]
        assert agg2 == case["result2"]


def test_archived_stream_multithread():
    for case in cases:
        stream = LiveChat(video_id=case["video_id"], seektime=case["seektime"])
        while stream.is_alive():
            chat = stream.get()
            agg1 = {}
            agg2 = {}
            for c in chat.items:
                if c.type in agg1:
                    agg1[c.type] += 1
                else:
                    agg1[c.type] = 1
                if c.author.type in agg2:
                    agg2[c.author.type] += 1
                else:
                    agg2[c.author.type] = 1
            break
        assert agg1 == case["result1"]
        assert agg2 == case["result2"]
    
def test_async_live_stream():
    async def test_loop(): 
        for case in cases:
            stream = LiveChatAsync(video_id=case["video_id"], seektime=case["seektime"])
            while stream.is_alive():
                chat = await stream.get()
                agg1 = {}
                agg2 = {}
                for c in chat.items:
                    if c.type in agg1:
                        agg1[c.type] += 1
                    else:
                        agg1[c.type] = 1
                    if c.author.type in agg2:
                        agg2[c.author.type] += 1
                    else:
                        agg2[c.author.type] = 1
                break
            assert agg1 == case["result1"]
            assert agg2 == case["result2"]
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(test_loop())
    except CancelledError:
        assert True
