from base64 import urlsafe_b64encode as b64enc
from functools import reduce
import calendar, datetime, pytz
import math
import random
import urllib.parse

'''
Generate continuation parameter of youtube replay chat.

Author: taizan-hokuto (2019) @taizan205

ver 0.0.1 2019.10.05
'''

def _gen_vid(video_id):
    """generate video_id parameter.
    Parameter
    ---------
        video_id : str

    Return
    ---------
    byte[] : base64 encoded video_id parameter.
    """
    header_magic = b'\x0A\x0F\x1A\x0D\x0A'
    header_id =  video_id.encode()
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
        b64enc(reduce(lambda x, y: x+y, item)).decode()
    ).encode()

def _nval(val):
    """convert value to byte array"""
    if val<0: raise ValueError
    buf = b''
    while val >> 7:
        m = val & 0xFF | 0x80
        buf += m.to_bytes(1,'big')
        val >>= 7
    buf += val.to_bytes(1,'big')
    return buf


def _tzparity(video_id,times):
    t=0
    for i,s in enumerate(video_id):
        ss = ord(s)
        if(ss % 2 == 0):
            t += ss*(12-i)
        else:
            t ^= ss*i

    return ((times^t) % 2).to_bytes(1,'big')


def _build(video_id, seektime, topchatonly = False):
    switch_01 = b'\x04' if topchatonly else b'\x01'


    if seektime < 0:
        raise ValueError('seektime is 0 or positive number.')
    if seektime == 0:  
        times =_nval(1)
        switch = b'\x04'       
    else:
        times =_nval(int(seektime*1000000))
        switch = b'\x03'
    parity = _tzparity(video_id, seektime)

    header_magic= b'\xA2\x9D\xB0\xD3\x04'
    sep_0       = b'\x1A'
    vid         = _gen_vid(video_id)
    time_tag    = b'\x28'
    timestamp1  = times
    sep_1       = b'\x30\x00\x38\x00\x40\x00\x48'
    sep_2       = b'\x52\x1C\x08\x00\x10\x00\x18\x00\x20\x00'
    chkstr      = b'\x2A\x0E\x73\x74\x61\x74\x69\x63\x63\x68\x65\x63\x6B\x73\x75\x6D\x40'
    sep_3       = b'\x00\x58\x03\x60'
    sep_4       = b'\x68'+parity+b'\x72\x04\x08'
    sep_5       = b'\x10'+parity+b'\x78\x00'
    body = [
        sep_0,
        _nval(len(vid)),
        vid,
        time_tag,
        timestamp1,
        sep_1,
        switch,
        sep_2,
        chkstr,
        sep_3,
        switch_01,
        sep_4,
        switch_01,
        sep_5
    ]

    body = reduce(lambda x, y: x+y, body)
    
    return  urllib.parse.quote(
                b64enc( header_magic +
                        _nval(len(body)) +
                        body
                ).decode()
            )

def getparam(video_id, seektime = 0):
    '''
    Parameter
    ---------
    seektime : int
        unit:seconds
        start position of fetching chat data.
    '''
    return _build(video_id, seektime)
