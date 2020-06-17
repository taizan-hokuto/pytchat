from .pb.header_pb2 import Header
from .pb.replay_pb2 import Continuation
from urllib.parse import quote
import base64

'''
Generate continuation parameter of youtube replay chat.

Author: taizan-hokuto

ver 0.0.1 2019.10.05 : Initial release.
ver 0.0.2 2020.05.30 : Use Protocol Buffers.
'''


def _gen_vid(video_id) -> str:
    header = Header()
    header.info.video.id = video_id
    header.terminator = 1
    return base64.urlsafe_b64encode(header.SerializeToString()).decode()


def _build(video_id, seektime, topchat_only) -> str:
    chattype = 1
    timestamp = 0
    if topchat_only:
        chattype = 4

    fetch_before_start = 3
    if seektime < 0:
        fetch_before_start = 4
    elif seektime == 0:
        timestamp = 1
    else:
        timestamp = int(seektime * 1000000)
    continuation = Continuation()
    entity = continuation.entity
    entity.header = _gen_vid(video_id)
    entity.timestamp = timestamp
    entity.s6 = 0
    entity.s7 = 0
    entity.s8 = 0
    entity.s9 = fetch_before_start
    entity.s10 = ''
    entity.s12 = chattype
    entity.chattype.value = chattype
    entity.s15 = 0
    return quote(
        base64.urlsafe_b64encode(continuation.SerializeToString()).decode())


def getparam(video_id, seektime=-1, topchat_only=False) -> str:
    '''
    Parameter
    ---------
    seektime : int
        unit:seconds
        start position of fetching chat data.
    topchat_only : bool
        if True, fetch only 'top chat'
    '''
    return _build(video_id, seektime, topchat_only)
