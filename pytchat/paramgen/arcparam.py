from . import enc
from base64 import urlsafe_b64encode as b64enc
from urllib.parse import quote


def _header(video_id) -> str:
    channel_id = '_' * 24
    S1_3 = enc.rs(1, video_id)
    S1_5 = enc.rs(1, channel_id) + enc.rs(2, video_id)
    S1 = enc.rs(3, S1_3) + enc.rs(5, S1_5)
    S3 = enc.rs(48687757, enc.rs(1, video_id))
    header_replay = enc.rs(1, S1) + enc.rs(3, S3) + enc.nm(4, 1)
    return b64enc(header_replay)


def _build(video_id, seektime, topchat_only) -> str:
    chattype = 4 if topchat_only else 1
    fetch_before_start = 3
    timestamp = 1000
    if seektime < 0:
        fetch_before_start = 4
    elif seektime == 0:
        timestamp = 1000
    else:
        timestamp = int(seektime * 1000000)
    header = enc.rs(3, _header(video_id))
    timestamp = enc.nm(5, timestamp)
    s6 = enc.nm(6, 0)
    s7 = enc.nm(7, 0)
    s8 = enc.nm(8, 0)
    s9 = enc.nm(9, fetch_before_start)
    s10 = enc.rs(10, enc.nm(4, 0))
    chattype = enc.rs(14, enc.nm(1, chattype))
    s15 = enc.nm(15, 0)
    entity = b''.join((header, timestamp, s6, s7, s8, s9, s10, chattype, s15))
    continuation = enc.rs(156074452, entity)
    return quote(b64enc(continuation).decode())


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
