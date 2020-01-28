from base64 import urlsafe_b64encode as b64enc
from functools import reduce
import time
import random
import urllib.parse

'''
Generate continuation parameter of youtube live chat.

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
    header_magic = b'\x0A\x0F\x0A\x0D\x0A'
    header_id =  video_id.encode()
    header_sep_1 = b'\x1A'
    header_sep_2 = b'\x43\xAA\xB9\xC1\xBD\x01\x3D\x0A'
    header_suburl = ('https://www.youtube.com/live_chat?v='
                    f'{video_id}&is_popout=1').encode()
    header_terminator = b'\x20\x02'

    item = [
        header_magic,
        _nval(len(header_id)),
        header_id,
        header_sep_1,
        header_sep_2,
        _nval(len(header_suburl)),
        header_suburl,
        header_terminator
    ]

    return urllib.parse.quote(
        b64enc(reduce(lambda x, y: x+y, item)).decode()
    ).encode()

def _tzparity(video_id,times):
    t=0
    for i,s in enumerate(video_id):
        ss = ord(s)
        if(ss % 2 == 0):
            t += ss*(12-i)
        else:
            t ^= ss*i

    return ((times^t) % 2).to_bytes(1,'big')

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

def _build(video_id, _ts1, _ts2, _ts3, _ts4, _ts5, topchat_only):
    #_short_type2
    switch_01 = b'\x04' if topchat_only else b'\x01'
    parity = _tzparity(video_id, _ts1^_ts2^_ts3^_ts4^_ts5)

    header_magic= b'\xD2\x87\xCC\xC8\x03'
    sep_0       = b'\x1A'
    vid         = _gen_vid(video_id)
    time_tag    = b'\x28'
    timestamp1  = _nval(_ts1)
    sep_1       = b'\x30\x00\x38\x00\x40\x02\x4A'
    un_len      = b'\x2B'
    sep_2       = b'\x08'+parity+b'\x10\x00\x18\x00\x20\x00'
    chkstr      = b'\x2A\x0E\x73\x74\x61\x74\x69\x63\x63\x68\x65\x63\x6B\x73\x75\x6D'
    sep_3       = b'\x3A\x00\x40\x00\x4A'
    sep_4_len   = b'\x02'
    sep_4       = b'\x08\x01'
    ts_2_start  = b'\x50'
    timestamp2  = _nval(_ts2)
    ts_2_end    = b'\x58'
    sep_5       = b'\x03'
    ts_3_start  = b'\x50'
    timestamp3  = _nval(_ts3)
    ts_3_end    = b'\x58'
    timestamp4  = _nval(_ts4)
    sep_6       = b'\x68'
    #switch
    sep_7       = b'\x82\x01\x04\x08'
    #switch
    sep_8       = b'\x10\x00'
    sep_9       = b'\x88\x01\x00\xA0\x01'
    timestamp5  = _nval(_ts5)

    body = [
        sep_0,
        _nval(len(vid)),
        vid,
        time_tag,
        timestamp1,
        sep_1,
        un_len,
        sep_2,
        chkstr,
        sep_3,
        sep_4_len,
        sep_4,
        ts_2_start,
        timestamp2,
        ts_2_end,
        sep_5,
        ts_3_start,
        timestamp3,
        ts_3_end,
        timestamp4,
        sep_6,
        switch_01,#
        sep_7,
        switch_01,#
        sep_8,
        sep_9,
        timestamp5
    ]

    body = reduce(lambda x, y: x+y, body)
    
    return  urllib.parse.quote(
                b64enc( header_magic +
                        _nval(len(body)) +
                        body
                ).decode()
            )

    
def _times(past_sec):
    
    n = int(time.time())
    
    _ts1= n - random.uniform(0,1*3)    
    _ts2= n - random.uniform(0.01,0.99)    
    _ts3= n - past_sec + random.uniform(0,1)
    _ts4= n - random.uniform(10*60,60*60)         
    _ts5= n - random.uniform(0.01,0.99)
    return list(map(lambda x:int(x*1000000),[_ts1,_ts2,_ts3,_ts4,_ts5]))


def getparam(video_id, past_sec = 0, topchat_only = False):
    '''
    Parameter
    ---------
    past_sec : int
        seconds to load past chat data
    topchat_only : bool
        if True, fetch only 'top chat'
    '''
    return _build(video_id,*_times(past_sec),topchat_only)

