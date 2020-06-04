from base64 import urlsafe_b64encode as b64enc
from functools import reduce
import urllib.parse

'''
Generate continuation parameter of youtube replay chat.

Author: taizan-hokuto (2019) @taizan205

ver 0.0.1 2019.10.05
'''


def _gen_vid_long(video_id):
    """generate video_id parameter.
    Parameter
    ---------
        video_id : str

    Return
    ---------
    byte[] : base64 encoded video_id parameter.
    """
    header_magic = b'\x0A\x0F\x1A\x0D\x0A'
    header_id = video_id.encode()
    header_sep_1 = b'\x1A\x13\xEA\xA8\xDD\xB9\x01\x0D\x0A\x0B'
    header_terminator = b'\x20\x01'

    item = [
        header_magic,
        _nval(len(header_id)),
        header_id,
        header_sep_1,
        header_id,
        header_terminator
    ]

    return urllib.parse.quote(
        b64enc(reduce(lambda x, y: x + y, item)).decode()
    ).encode()


def _gen_vid(video_id):
    """generate video_id parameter.
    Parameter
    ---------
        video_id : str

    Return
    ---------
        bytes : base64 encoded video_id parameter.
    """
    header_magic = b'\x0A\x0F\x1A\x0D\x0A'
    header_id = video_id.encode()
    header_terminator = b'\x20\x01'

    item = [
        header_magic,
        _nval(len(header_id)),
        header_id,
        header_terminator
    ]

    return urllib.parse.quote(
        b64enc(reduce(lambda x, y: x + y, item)).decode()
    ).encode()


def _nval(val):
    """convert value to byte array"""
    if val < 0:
        raise ValueError
    buf = b''
    while val >> 7:
        m = val & 0xFF | 0x80
        buf += m.to_bytes(1, 'big')
        val >>= 7
    buf += val.to_bytes(1, 'big')
    return buf


def _build(video_id, seektime, topchat_only):
    switch_01 = b'\x04' if topchat_only else b'\x01'
    if seektime < 0:
        raise ValueError("seektime must be greater than or equal to zero.")
    if seektime == 0:
        times = b''
    else:
        times = _nval(int(seektime * 1000))
    if seektime > 0:
        _len_time = b'\x5A' + (len(times) + 1).to_bytes(1, 'big') + b'\x10'
    else:
        _len_time = b''

    header_magic = b'\xA2\x9D\xB0\xD3\x04'
    sep_0 = b'\x1A'
    vid = _gen_vid(video_id)
    _tag = b'\x40\x01'
    timestamp1 = times
    sep_1 = b'\x60\x04\x72\x02\x08'
    terminator = b'\x78\x01'

    body = [
        sep_0,
        _nval(len(vid)),
        vid,
        _tag,
        _len_time,
        timestamp1,
        sep_1,
        switch_01,
        terminator
    ]

    body = reduce(lambda x, y: x + y, body)

    return urllib.parse.quote(
        b64enc(header_magic + _nval(len(body)) + body
               ).decode()
    )


def getparam(video_id, seektime=0.0, topchat_only=False):
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
