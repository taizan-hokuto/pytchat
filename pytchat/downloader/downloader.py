import asyncio
import aiohttp,async_timeout
import json
import traceback,time
from urllib.parse import quote

from . import parser
from .. import config
from .. import util
from .. paramgen import arcparam

logger = config.logger(__name__)
headers=config.headers

REPLAY_URL = "https://www.youtube.com/live_chat_replay/" \
             "get_live_chat_replay?continuation="


class Block:
    def __init__(self, pos=0, init_offset=0, last_offset=0,
                 continuation='', chat_data=[]):
        self.pos = pos
        self.init_offset = init_offset
        self.last_offset = last_offset
        self.stop_offset = 0
        self.continuation = continuation
        self.chat_data = chat_data

def _debug_save(_pbar_pos,prefix,init_offset_ms,last_offset_ms,dics):
    chat_data =[]
    init = '{:0>8}'.format(str(init_offset_ms))
    last = '{:0>8}'.format(str(last_offset_ms))
    chat_data.extend(dics["response"]["continuationContents"]["liveChatContinuation"]["actions"])
        
    with open(f"[{_pbar_pos}]-{prefix}-from_{init}_to_{last}.data",mode ='w',encoding='utf-8') as f:
        f.writelines(chat_data)

        
def dump(o):
    for key, value in o.__dict__.items():
        if key != "chat_data":
            print(key, ':', value)

def dumpt(blocks,mes = None):
    print(f"{'-'*40}\n{mes}")
    [print(f"pos:{b.pos:>2}   |init:{b.init_offset: >12,}   |last:{b.last_offset: >12,}   |stop:{b.stop_offset :>12,} ")
        for b in blocks]

def _divide_(start, end, count):
    min_interval = 120
    if (not isinstance(start,int) or 
        not isinstance(end,int) or 
        not isinstance(count,int)):
        raise ValueError("start/end/count must be int")
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


def ready_blocks(video_id:str, div:int, duration:int):
    if div <= 0: raise ValueError

    def _divide(start, end, count):
        if (not isinstance(start,int) or 
            not isinstance(end,int) or 
            not isinstance(count,int)):
            raise ValueError("start/end/count must be int")
        if start>end:
            raise ValueError("end must be equal to or greater than start.")
        if count<1:
            raise ValueError("count must be equal to or greater than 1.")

        interval= (end-start)/(count) 
        if interval < 120 :
            interval=120
            count = int((end-start)/interval)+1
        if count == 1:
            return [start]
        return sorted(list(set([int(start+interval*j)
            if j < count else end 
            for j in range(count) ])))

    async def _get_blocks(duration,div):
        async with aiohttp.ClientSession() as session:
            futures = [_create_block(session, pos, seektime)
                for pos, seektime in enumerate(_divide(-1, duration , div))]
            return await asyncio.gather(*futures,return_exceptions=True)

    async def _create_block(session, pos, seektime):
        continuation = arcparam.getparam(video_id,seektime=seektime)
        url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"

        async with session.get(url,headers = headers) as resp:
            text = await resp.text()
        #util.save(text,f"v:/~~/pre_{pos}_",".json")
        next_continuation, actions = parser.parse(json.loads(text))
        block = Block(
            pos = pos,
            continuation = next_continuation,
            chat_data = actions,
            init_offset = parser.get_offset(actions[0]),
            last_offset = parser.get_offset(actions[-1])
        )
        return block

    blocks=[]
    loop = asyncio.get_event_loop()
    blocks = loop.run_until_complete(_get_blocks(duration,div))
    return blocks  

def remove_duplicate_head(blocks):
    def is_same_offset(index):
        return (blocks[index].init_offset == blocks[index+1].init_offset)

    def is_same_id(index):
        id_0 = parser.get_id(blocks[index].chat_data[0])
        id_1 = parser.get_id(blocks[index+1].chat_data[0])
        return (id_0 == id_1)

    def is_same_type(index):
        type_0 = parser.get_type(blocks[index].chat_data[0])
        type_1 = parser.get_type(blocks[index+1].chat_data[0])
        return (type_0 == type_1)

    ret = []
    [ret.append(blocks[i]) for i in range(len(blocks)-1)
        if (len(blocks[i].chat_data)>0 and 
        not ( is_same_offset(i) and is_same_id(i) and is_same_type(i)))]
    ret.append(blocks[-1])
    blocks = None
    return ret

def remove_overwrap(blocks):
    def is_overwrap(a, b):
        print(f"comparing({a}, {b})....overwrap ({(blocks[a].last_offset > blocks[b].init_offset)})")
        return (blocks[a].last_offset > blocks[b].init_offset)
    
    ret = []
    a = 0
    b=1
    jmp = False
    ret.append(blocks[0])
    while a < len(blocks)-2:

        while is_overwrap(a,b):
            b+=1
            print("forward")
            if b == len(blocks)-2:
                jmp=True    
                break
        if jmp: break
        if b-a == 1:
            print(f"next  ret.append(blocks[{b}]")
            ret.append(blocks[b])
            a = b
            b+=1

            continue
        else:
            print(f"apart ret.append(blocks[{b-1}]")
            ret.append(blocks[b-1])
            a=b-1
            b=a+1
    ret.append(blocks[-1])            
    return ret

def remove_duplicate_tail(blocks):
    def is_same_offset(index):
        return blocks[index-1].init_offset == blocks[index].init_offset

    def is_same_id(index):
        id_0 = parser.get_id(blocks[index-1].chat_data[-1])
        id_1 = parser.get_id(blocks[index].chat_data[-1])
        return id_0 == id_1

    def is_same_type(index):
        type_0 = parser.get_type(blocks[index-1].chat_data[-1])
        type_1 = parser.get_type(blocks[index].chat_data[-1])
        return type_0 == type_1

    ret = []
    [ret.append(blocks[i]) for i in range(len(blocks)-1)
        if not ( is_same_offset(i) and is_same_id(i) and is_same_type(i) )]
    ret.append(blocks[-1])
    blocks = None
    return ret
    

def set_stop_offset(blocks):
    for i in range(len(blocks)-1):
        blocks[i].stop_offset = blocks[i+1].init_offset
    blocks[-1].stop_offset = -1
    return blocks


def download_each_block(blocks):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_dl_block(blocks))

async def _dl_block(blocks):
    futures = []
    async with aiohttp.ClientSession() as session:
        futures = [_dl_chunk(session, block) for block in blocks]
        return await asyncio.gather(*futures,return_exceptions=True)    

async def _dl_chunk(session, block:Block):
    if (block.stop_offset != -1 and
        block.last_offset > block.stop_offset):
        return 

    def get_last_offset(actions):
        return parser.get_offset(actions[-1])

    continuation = block.continuation
    while continuation:
        print(block.pos)
        url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
        async with session.get(url,headers = config.headers) as resp:
            text = await resp.text()
        continuation, actions = parser.parse(json.loads(text))
        if actions:
            block.chat_data.extend(actions)
            last_offset = get_last_offset(actions)
            if block.stop_offset != -1:
                if last_offset > block.stop_offset:
                    block.last_offset = last_offset
                    break
            else:
                block.last_offset = last_offset


def combine(blocks):
    line = ''
    try:
        if len(blocks[0].chat_data)>0:
            lastline=blocks[0].chat_data[-1]
            lastline_offset = parser.get_offset(lastline)
        else: return None
        for i in range(1,len(blocks)):
            f=blocks[i].chat_data
            if len(f)==0:
                logger.error(f'zero size piece.:{str(i)}')
                continue
            for row in range(len(f)):
                line = f[row]
                if parser.get_offset(line) > lastline_offset:
                    blocks[0].chat_data.extend(f[row:])
                    break
                if line =='error':
                    logger.error(f'Error file was saved.: piece:{str(i)}')
                    return['error']
            else:
                logger.error(f'Missing common line.: piece:{str(i-1)}->{str(i)} lastline_id= {lastline_offset}')
                return ['combination failed']
            lastline_offset = parser.get_offset( f[-1])
        return blocks[0].chat_data
    except Exception as e:
        logger.error(f"{type(e)} {str(e)} {line}")
        traceback.print_exc()
        

def download(video_id, duration, div):
    blocks = ready_blocks(video_id=video_id, duration=duration, div=div)
    dumpt(blocks,"ready_blocks")

    selected = remove_duplicate_head(blocks)
    dumpt(selected,"removed duplicate_head")
    
    
    set_stop_offset(selected)
    dumpt(selected,"set stop_offset")
    #set_stop_offset(selected)
    removed = remove_overwrap(selected)
    dumpt(removed,"removed overwrap")   
     
    download_each_block(removed)
    dumpt(removed,"downloaded each_block")

    return combine(removed)