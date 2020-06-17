from .pb.header_pb2 import Header
from .pb.live_pb2 import Continuation
from urllib.parse import quote
import base64
import random
import time

'''
Generate continuation parameter of youtube live chat.

Author: taizan-hokuto

ver 0.0.1 2019.10.05 : Initial release.
ver 0.0.2 2020.05.30 : Use Protocol Buffers.
'''


def _gen_vid(video_id) -> str:
    """generate video_id parameter.
    Parameter
    ---------
        video_id : str

    Return
    ---------
    str : base64 encoded video_id parameter.
    """
    header = Header()
    header.info.video.id = video_id
    header.terminator = 1
    return base64.urlsafe_b64encode(header.SerializeToString()).decode()


def _build(video_id, ts1, ts2, ts3, ts4, ts5, topchat_only) -> str:
    chattype = 1
    if topchat_only:
        chattype = 4
    continuation = Continuation()
    entity = continuation.entity

    entity.header = _gen_vid(video_id)
    entity.timestamp1 = ts1
    entity.s6 = 0
    entity.s7 = 0
    entity.s8 = 1
    entity.body.b1 = 0
    entity.body.b2 = 0
    entity.body.b3 = 0
    entity.body.b4 = 0
    entity.body.b7 = ''
    entity.body.b8 = 0
    entity.body.b9 = ''
    entity.body.timestamp2 = ts2
    entity.body.b11 = 3
    entity.body.b15 = 0
    entity.timestamp3 = ts3
    entity.timestamp4 = ts4
    entity.s13 = chattype
    entity.chattype.value = chattype
    entity.s17 = 0
    entity.str19.value = 0
    entity.timestamp5 = ts5

    return quote(
        base64.urlsafe_b64encode(continuation.SerializeToString()).decode()
    )


def _times(past_sec):
    n = int(time.time())
    _ts1 = n - random.uniform(0, 1 * 3)
    _ts2 = n - random.uniform(0.01, 0.99)
    _ts3 = n - past_sec + random.uniform(0, 1)
    _ts4 = n - random.uniform(10 * 60, 60 * 60)
    _ts5 = n - random.uniform(0.01, 0.99)
    return list(map(lambda x: int(x * 1000000), [_ts1, _ts2, _ts3, _ts4, _ts5]))


def getparam(video_id, past_sec=0, topchat_only=False) -> str:
    '''
    Parameter
    ---------
    past_sec : int
        seconds to load past chat data
    topchat_only : bool
        if True, fetch only 'top chat'
    '''
    return _build(video_id, *_times(past_sec), topchat_only)
