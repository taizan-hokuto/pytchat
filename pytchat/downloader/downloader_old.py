import asyncio
import aiohttp,async_timeout
import json
from tqdm import tqdm
import traceback,time
from requests.exceptions import ConnectionError
from urllib.parse import quote
from multiprocessing import Process,  Queue

from . import dictquery
from .. import config
from .. paramgen import arcparam
from .. import util



logger = config.logger(__name__)

REPLAY_URL = "https://www.youtube.com/live_chat_replay/" \
             "get_live_chat_replay?continuation="

async def _dl_piece(_session,queue,movie_id,offset_ms,duration_ms,pbar_pos,is_lastpiece,dl_end):
    #print(f'_dl_piece:{movie_id},{offset_ms},{duration_ms},{pbar_pos},{is_lastpiece}')
    
    chat_data=[]
    if pbar_pos == 0:
        #continue_url = construct.encoder.encode(construct.construct_seekinit(movie_id,filter='all'))
        continuation = arcparam.getparam(movie_id,-1)
    else:
        continuation = arcparam.getparam(movie_id,offset_ms/1000)
    next_url = f"{REPLAY_URL}{quote(continuation)}&pbj=1"
        
    #print(pbar_pos,next_url)
    chat_data = await _dl(session=_session,
                        queue = queue,
                        next_url =next_url,
                        absolute_start = offset_ms,
                        duration = duration_ms,
                        pbar_pos = pbar_pos,
                        is_lastpiece = is_lastpiece,
                        dl_end = dl_end)
    return chat_data

def get_init_offset_ms(dics: dict):
    n = 0
    while(True):
        init_offset_ms = dics["response"]["continuationContents"]["liveChatContinuation"]["actions"][n].get("replayChatItemAction")['videoOffsetTimeMsec']
        if init_offset_ms is None:
            n += 1
            continue
        else:
            return int(init_offset_ms)

def get_last_offset_ms(dics: dict):
    m = -1                    
    while(True):
        last_offset_ms = dics["response"]["continuationContents"]["liveChatContinuation"]["actions"][m].get("replayChatItemAction")['videoOffsetTimeMsec']
        if last_offset_ms is None:
            m -= 1
            continue
        else:
            return int(last_offset_ms)
        

async def _dl(session,queue, next_url, absolute_start,duration,pbar_pos,is_lastpiece,dl_end):
    async with async_timeout.timeout(1000):
        chat_data = []
        #print('absolute',absolute_start,'duration',duration,'pos',pbar_pos)
        dlerror=False
        first = True
        rqerr=0
        jserr=0
        while(True):

            try:
                #json形式のchatデータのダウンロードと読み込み
                async with session.get(next_url,headers=config.headers) as response:
                    text = await response.text()
                    util.save(text,"v:/~~/test_",".json")
                    dics = json.loads(text)

                    continuation = dics["response"]["continuationContents"]["liveChatContinuation"]["continuations"][0]["liveChatReplayContinuationData"]["continuation"]
                    #次のlive_chat_replayのurl
                    next_url =f"{REPLAY_URL}{continuation}&pbj=1"

                    init_offset_ms = get_init_offset_ms(dics)
                    last_offset_ms = get_last_offset_ms(dics)
                    length_ms      = last_offset_ms - init_offset_ms
                    #print(f'[{pbar_pos}] length_ms = {length_ms}, total={last_offset_ms}')
                    if length_ms < 0:
                        raise Exception('length_ms < 0')
                    queue.put(length_ms)
                    if first:
                        #print(dics["response"]["continuationContents"]["liveChatContinuation"]["actions"][0])
                        #with open(str(pbar_pos)+'FIRST') as f:
                        #    f.writelines(dics)##############################
                        if pbar_pos > 0:
                            #print(f'Reset dl_end[{pbar_pos - 1}]:{dl_end[pbar_pos - 1]} -> {init_offset_ms} ({init_offset_ms-dl_end[pbar_pos - 1]})')
                            dl_end[pbar_pos - 1] = init_offset_ms
                        first = False
                    #print(dics["response"]["continuationContents"]["liveChatContinuation"]["actions"][0])
                    chat_data.extend(dics["response"]["continuationContents"]["liveChatContinuation"]["actions"])
                    #print(chat_data)
                    if (last_offset_ms >= dl_end[pbar_pos]) and not(is_lastpiece):
                        #save(pbar_pos,'LAST ',init_offset_ms,last_offset_ms,dics)###############################
                        #print(f'break:pbar_pos ={pbar_pos}')
                        queue.put('quit')
                        break

            # next_urlが入手できなくなったら終わり
            except KeyError:
                queue.put('quit')
                break
            # JSONDecodeErrorが発生した場合はデータを取得しなおす。
            except json.decoder.JSONDecodeError:
                time.sleep(1)
                jserr+=1
                if jserr<20:
                    continue
                else:
                    logger.error('JSONDecodeError at piece %d' % (pbar_pos))
                    queue.put(quit)
                    dlerror = True
                    break
            except ConnectionError:
                time.sleep(1)
                rqerr+=1
                if rqerr<20:
                    continue
                else:
                    logger.error('ConnectionError at piece %d' % (pbar_pos))
                    queue.put(quit)
                    dlerror = True
                    break
            #except KeyboardInterrupt:
            #    pass
            except UnicodeDecodeError as e:
                logger.error(f"{type(e)}, {str(e)}")
                logger.error(f"{str(e.object)}")
                with open('unicodeerror.txt', mode ="w", encoding='utf-8') as f:
                    f.writelines(str(e.object))
                break
            except:
                logger.error('\n不明なエラーが発生しました%d at:' % (pbar_pos))
                logger.error('%s\n' % (next_url))
                traceback.print_exc()
                try:
                    with open('error.json', mode ="w", encoding='utf-8') as f:
                        f.writelines(text)
                except UnboundLocalError as ule:
                    pass
                queue.put('quit')
                dlerror = True
                break
        #session.close()
        if dlerror:
            return 'error'
        else:
            return chat_data  


def _debug_save(_pbar_pos,prefix,init_offset_ms,last_offset_ms,dics):
    '''
    例外が発生したときのチャットデータを保存する。
    '''
    chat_data =[]
    init = '{:0>8}'.format(str(init_offset_ms))
    last = '{:0>8}'.format(str(last_offset_ms))
    chat_data.extend(dics["response"]["continuationContents"]["liveChatContinuation"]["actions"])
        
    with open(f"[{_pbar_pos}]-{prefix}-from_{init}_to_{last}.data",mode ='w',encoding='utf-8') as f:
        f.writelines(chat_data)

def _debug_chatblock():
    pass


async def _asyncdl(argslist):
    promises=[]
    async with aiohttp.ClientSession() as session:
        promises = [_dl_piece(session,*args) for args in argslist]
        return await asyncio.gather(*promises)

def _listener(q,duration,div):
    duration_ms =int(duration/1000)
    ret = int(div)
    pbar = tqdm(total = duration_ms, ncols=80,unit_scale = 1,
         bar_format='{desc}{percentage:3.0f}%|{bar}|[{n_fmt:>7}/{total_fmt}]{elapsed}<{remaining}')
    #Noneを見つけるまでgetし続ける。
    
    for item in iter(q.get, None):
        if(item=='quit'):
            ret=ret-1
            if(ret==0):
                if duration_ms>0:
                    pbar.update(duration_ms)
                pbar.close()
        else:
            item =int(item/1000)
            if duration_ms - item >= 0 and  item >= 0:
                duration_ms -= item
                pbar.update(item) 


def _combine(chatblocks):
    '''
    分割DLしたチャットデータを結合する
    1番目の固まり(chatblocks[0])に順次結合していく。
    '''
    line=''
    try:
        if len(chatblocks[0])>0:
            lastline=chatblocks[0][-1]
            #lastline_id = dictquery.getid_replay(json.loads(lastline))
            lastline_id = dictquery.getid_replay(lastline)
        else: return None
        for i in range(1,len(chatblocks)):
            f=chatblocks[i]
            if len(f)==0:
                logger.error(f'zero size piece.:{str(i)}')
                continue
            #チャットデータの行を最初から走査して直前のデータの末尾との共通行を探す
            for row in range(len(f)):
                #row行目のデータ
                line = f[row]
                #末尾が直前のデータの末尾行と等しい（ダウンロードタイミングが異なると
                #trackingParamsが一致しないためidで判定）
                #if dictquery.getid_replay(json.loads(line)) == lastline_id:
                if dictquery.getid_replay(line) == lastline_id:
                    #共通行が見つかったので、共通行以降を結合する
                    #print(f'[{i}][{row}]Find common line {lastline_id}')
                    chatblocks[0].extend(f[row+1:])
                    break
                if line =='error':
                    logger.error(f'Error file was saved.: piece:{str(i)}')
                    return['error']
            else:#forの途中でbreakが発生しなかった場合ここに飛ぶ
                #ファイルの結合点（共通ライン）の発見に失敗
                logger.error(f'Missing common line.: piece:{str(i-1)}->{str(i)} lastline_id= {lastline_id}')
                return ['combination failed']#---------------------------------test
            #最終行のデータを更新する
            lastline = f[-1]
            #dic_lastline=json.loads(lastline)
            dic_lastline=lastline
            lastline_id = dictquery.getid_replay(dic_lastline)
            #print(f'[{i}]lastline_id:{lastline_id}')
        print(f"length:{len(chatblocks[0])}")
        return chatblocks[0]
    except Exception as e:
        logger.error(f"{type(e)} {str(e)} {line}")
        traceback.print_exc()
        # p= json.loads(line)
        # with open('v:/~~/error_dic.json',mode ='w',encoding='utf-8') as f:
        #     f.write(line)


def download(movie_id, duration, divisions):
    #動画の長さ（ミリ秒）
    duration_ms=duration*1000
    #分割DL数
    div = divisions
    #プログレスバー用のQueue
    queue= Queue()
    #プログレスバー用のプロセス
    proc = Process(target=_listener,args=(queue,duration_ms,div))
    proc.start()
    #チャットデータの分割間隔(ミリ秒）
    term_ms = int(duration_ms / div)
    #チャットデータの取得開始時間
    start_ms = 0
    #分割したピースが最後かどうか
    is_lastpiece  = False
    argslist=[]
    dl_end=[]
    #分割DL用の引数を用意
    for i in range(0,div):
        if i==div-1:
            is_lastpiece =True
        args = (queue, movie_id, start_ms, term_ms, i, is_lastpiece,dl_end)
        argslist.append(args)
        start_ms+=term_ms
        dl_end.append(start_ms)

    loop = asyncio.get_event_loop()  
    chatlist =loop.run_until_complete(_asyncdl(argslist))
    #プログレスバーのプロセスを終了させるためQueueにNoneを送る
    queue.put(None)
    #分割DLされたチャットデータを結合して返す

    return _combine(chatlist)
 