import asyncio
from .listener import AsyncListener
from .. import config
from .. import mylogger
import datetime
import os
import aiohttp
import signal
import threading
from .buffer import Buffer
from  concurrent.futures import CancelledError
logger = mylogger.get_logger(__name__,mode=config.LOGGER_MODE)

class ListenManager:

    '''
    動画IDまたは動画IDのリストを受け取り、
    動画IDに対応したListenerを生成・保持する。

    #Attributes
    ----------
    _listeners: dict  
        ListenManegerがつかんでいるListener達のリスト.  
        key:動画ID value:動画IDに対応するListener
    _queue: Queue
        動画IDを外部から受け渡しするためのキュー
        _queueが空である間は、ノンブロッキングで他のタスクを実行
        _queueに動画IDが投入されると、_dequeueメソッドで
        直ちにListenerを生成し返す。
    _event: threading.Event
        キーボードのCTRL+Cを検知するためのEventオブジェクト
    '''
    def __init__(self,interruptable = True):
        #チャット監視中の動画リスト
        self._listeners={}
        self._tasks = []
        #外部からvideoを受け取るためのキュー
        self._queue = asyncio.Queue()
        self._event = threading.Event()
        self._ready_queue()
        self._is_alive = True
        #キーボードのCtrl+cを押したとき、_hundler関数を呼び出すように設定
        signal.signal(signal.SIGINT, (lambda a, b: self._handler(self._event, a, b)))

    def is_alive(self)->bool:
        '''
        ListenManagerが稼働中であるか。
            True->稼働中
            False->Ctrl+Cが押されて終了
        '''
        logger.debug(f'check is_alive() :{self._is_alive}')
        return self._is_alive
    
    def _handler(self, event, sig, handler):
        '''
        Ctrl+Cが押下されたとき、終了フラグをセットする。
        '''
        logger.debug('Ctrl+c pushed')
        self._is_alive = False
        logger.debug('terminating listeners.')
        for listener in self._listeners.values():
            listener.terminate()
        logger.debug('end.')


    def _ready_queue(self):
        #loop = asyncio.get_event_loop()
        self._tasks.append(
            asyncio.create_task(self._dequeue())
            )


    async def set_video_ids(self,video_ids:list):
        for video_id in video_ids:
            if video_id:
                await self._queue.put(video_id)


    async def get_listener(self,video_id) -> AsyncListener:
        return await self._create_listener(video_id)
            
    # async def getlivechat(self,video_id):
    #     '''
    #     指定された動画IDのチャットデータを返す

    #     Parameter
    #     ----------
    #     video_id: str
    #         動画ID

    #     Return
    #     ----------
    #         引数で受け取った動画IDに対応する
    #         Listenerオブジェクトへの参照
            
    #     '''
    #     logger.debug('manager get/create listener')
    #     listener = await self._create_listener(video_id)
    #     '''
    #     上が完了しないうちに、下が呼び出される
    #     '''
    #     if not listener._initialized:
    #         await asyncio.sleep(2)
    #         return []
    #     if listener:
    #         #listener._isfirstrun=False
    #         return await listener.getlivechat()
        


    async def _dequeue(self):
        '''
        キューに入った動画IDを
        Listener登録に回す。
        
        '''
        while True:
            video_id = await self._queue.get()
            #listenerを登録、タスクとして実行する
            logger.debug(f'deque got [{video_id}]')
            await self._create_listener(video_id)

    async def _create_listener(self, video_id) -> AsyncListener:
        '''
        Listenerを作成しチャット取得中リストに加え、
        Listenerを返す
        '''
        if video_id is None or not isinstance(video_id, str):
            raise TypeError('video_idは文字列でなければなりません')
        if video_id in self._listeners:
            return self._listeners[video_id]
        else:
            #listenerを登録する
            listener = AsyncListener(video_id,interruptable = False,buffer = Buffer())
            self._listeners.setdefault(video_id,listener)
            #task = asyncio.ensure_future(listener.initialize())
            #await asyncio.gather(listener.initialize())
            #task.add_done_callback(self.finish)
            #await listener.initialize()
            #self._tasks.append(task)

            return listener

 
    def finish(self,sender):
        try:
            if sender.result():
                video_id = sender.result()[0]
                message = sender.result()[1]
            
                #listener終了時のコールバック        
                #sender.result()[]でデータを取得できる
                logger.info(f'終了しました VIDEO_ID:[{video_id}] message:{message}')
                #logger.info(f'終了しました')
                if video_id in self._listeners:
                    self._listeners.pop(video_id)
        except CancelledError:
            logger.debug('cancelled.')

    def get_listeners(self):
        return self._listeners

    def shutdown(self):
        '''
        ListenManegerを終了する
        '''
        logger.debug("start shutdown")
        self._is_alive =False
        try:
            #Listenerを停止する。
            for listener in self._listeners.values():
                listener.terminate()
            #taskをキャンセルする。
            for task in self._tasks:
                if not task.done():
                    #print(task)
                    task.cancel()
        except Exception as er:
            logger.info(str(er),type(er))

        logger.debug("finished.")

    def get_tasks(self):
        return self._tasks