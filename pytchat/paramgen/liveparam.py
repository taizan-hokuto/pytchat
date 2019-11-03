from base64 import urlsafe_b64encode as b64enc
from functools import reduce
import calendar, datetime, pytz
import math
import random
import urllib.parse


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

def _build(video_id, _ts1, _ts2, _ts3, _ts4, _ts5, topchatonly = False):
    #_short_type2
    switch_01 = b'\x04' if topchatonly else b'\x01'
    header_magic= b'\xD2\x87\xCC\xC8\x03'

    sep_0       = b'\x1A'
    vid         = _gen_vid(video_id)
    time_tag    = b'\x28'
    timestamp1  = _nval(_ts1)
    sep_1       = b'\x30\x00\x38\x00\x40\x02\x4A'
    un_len      = b'\x2B'
    sep_2       = b'\x08\x00\x10\x00\x18\x00\x20\x00'
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

    
def _times():
    
    def unixts_now():
        now = datetime.datetime.now(pytz.utc)
        return calendar.timegm(now.utctimetuple())

    n = unixts_now()
    
    _ts1= n - random.uniform(0,1*3)    
    _ts2= n - random.uniform(0.01,0.99)    
    _ts3= n - 60+random.uniform(0,1)
    _ts4= n - random.uniform(10*60,60*60)         
    _ts5= n - random.uniform(0.01,0.99)
    return list(map(lambda x:int(x*1000000),[_ts1,_ts2,_ts3,_ts4,_ts5]))


def getparam(video_id):
    return _build(video_id,*_times())

