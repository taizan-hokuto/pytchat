import httpx
import json
import signal
import time
import traceback
import urllib.parse
from concurrent.futures import CancelledError, ThreadPoolExecutor
from queue import Queue
from threading import Event
from .buffer import Buffer
from ..parser.live import Parser
from .. import config
from .. import exceptions
from ..paramgen import liveparam, arcparam
from ..processors.default.processor import DefaultProcessor
from ..processors.combinator import Combinator
from ..util.extract_video_id import extract_video_id

headers = config.headers
MAX_RETRY = 10


class LiveChat:
    ''' スレッドプールを利用してYouTubeのライブ配信のチャットデータを取得する

    Parameter
    ---------
    video_id : str
        動画ID

    seektime : int
        （ライブチャット取得時は無視）
        取得開始するアーカイブ済みチャットの経過時間(秒）
        マイナス値を指定した場合は、配信開始前のチャットも取得する。

    processor : ChatProcessor
        チャットデータを加工するオブジェクト

    buffer : Buffer(maxsize:20[default])
        チャットデータchat_componentを格納するバッファ。
        maxsize : 格納できるchat_componentの個数
        default値20個。1個で約5~10秒分。

    interruptable : bool
        Ctrl+Cによる処理中断を行うかどうか。

    callback : func
        _listen()関数から一定間隔で自動的に呼びだす関数。

    done_callback : func
        listener終了時に呼び出すコールバック。

    direct_mode : bool
        Trueの場合、bufferを使わずにcallbackを呼ぶ。
        Trueの場合、callbackの設定が必須
        (設定していない場合IllegalFunctionCall例外を発生させる）

    force_replay : bool
        Trueの場合、ライブチャットが取得できる場合であっても
        強制的にアーカイブ済みチャットを取得する。

    topchat_only : bool
        Trueの場合、上位チャットのみ取得する。

    Attributes
    ---------
    _executor : ThreadPoolExecutor
        チャットデータ取得ループ（_listen）用のスレッド

    _is_alive : bool
        チャット取得を停止するためのフラグ
    '''

    _setup_finished = False

    def __init__(self, video_id,
                 seektime=-1,
                 processor=DefaultProcessor(),
                 buffer=None,
                 interruptable=True,
                 callback=None,
                 done_callback=None,
                 direct_mode=False,
                 force_replay=False,
                 topchat_only=False,
                 logger=config.logger(__name__)
                 ):
        self._video_id = extract_video_id(video_id)
        self.seektime = seektime
        if isinstance(processor, tuple):
            self.processor = Combinator(processor)
        else:
            self.processor = processor
        self._buffer = buffer
        self._callback = callback
        self._done_callback = done_callback
        self._executor = ThreadPoolExecutor(max_workers=2)
        self._direct_mode = direct_mode
        self._is_alive = True
        self._is_replay = force_replay
        self._parser = Parser(is_replay=self._is_replay)
        self._pauser = Queue()
        self._pauser.put_nowait(None)
        self._first_fetch = True
        self._fetch_url = "live_chat/get_live_chat?continuation="
        self._topchat_only = topchat_only
        self._event = Event()
        self._logger = logger
        self.exception = None
        if interruptable:
            signal.signal(signal.SIGINT, lambda a, b: self.terminate())
        self._setup()

    def _setup(self):
        # direct modeがTrueでcallback未設定の場合例外発生。
        if self._direct_mode:
            if self._callback is None:
                raise exceptions.IllegalFunctionCall(
                    "When direct_mode=True, callback parameter is required.")
        else:
            # direct modeがFalseでbufferが未設定ならばデフォルトのbufferを作成
            if self._buffer is None:
                self._buffer = Buffer(maxsize=20)
                # callbackが指定されている場合はcallbackを呼ぶループタスクを作成
            if self._callback is None:
                pass
            else:
                # callbackを呼ぶループタスクの開始
                self._executor.submit(self._callback_loop, self._callback)
        # _listenループタスクの開始
        self.listen_task = self._executor.submit(self._startlisten)
        # add_done_callbackの登録
        if self._done_callback is None:
            self.listen_task.add_done_callback(self._finish)
        else:
            self.listen_task.add_done_callback(self._done_callback)

    def _startlisten(self):
        time.sleep(0.1)  # sleep shortly to prohibit skipping fetching data
        """Fetch first continuation parameter,
        create and start _listen loop.
        """
        initial_continuation = liveparam.getparam(self._video_id, 3)
        self._listen(initial_continuation)

    def _listen(self, continuation):
        ''' Fetch chat data and store them into buffer,
        get next continuaiton parameter and loop.

        Parameter
        ---------
        continuation : str
            parameter for next chat data
        '''
        try:
            with httpx.Client(http2=True) as client:
                while(continuation and self._is_alive):
                    continuation = self._check_pause(continuation)
                    contents = self._get_contents(continuation, client, headers)
                    metadata, chatdata = self._parser.parse(contents)
                    timeout = metadata['timeoutMs'] / 1000
                    chat_component = {
                        "video_id": self._video_id,
                        "timeout": timeout,
                        "chatdata": chatdata
                    }
                    time_mark = time.time()
                    if self._direct_mode:
                        processed_chat = self.processor.process(
                            [chat_component])
                        if isinstance(processed_chat, tuple):
                            self._callback(*processed_chat)
                        else:
                            self._callback(processed_chat)
                    else:
                        self._buffer.put(chat_component)
                    diff_time = timeout - (time.time() - time_mark)
                    self._event.wait(diff_time if diff_time > 0 else 0)
                    continuation = metadata.get('continuation')
        except exceptions.ChatParseException as e:
            self._logger.debug(f"[{self._video_id}]{str(e)}")
            raise
        except (TypeError, json.JSONDecodeError):
            self._logger.error(f"{traceback.format_exc(limit=-1)}")
            raise

        self._logger.debug(f"[{self._video_id}]finished fetching chat.")
        raise exceptions.ChatDataFinished

    def _check_pause(self, continuation):
        if self._pauser.empty():
            '''pause'''
            self._pauser.get()
            '''resume:
                prohibit from blocking by putting None into _pauser.
            '''
            self._pauser.put_nowait(None)
            if not self._is_replay:
                continuation = liveparam.getparam(self._video_id, 3)
        return continuation

    def _get_contents(self, continuation, client, headers):
        '''Get 'continuationContents' from livechat json.
           If contents is None at first fetching,
           try to fetch archive chat data.

          Return:
          -------
            'continuationContents' which includes metadata & chat data.
        '''
        livechat_json = (
            self._get_livechat_json(continuation, client, headers)
        )
        contents = self._parser.get_contents(livechat_json)
        if self._first_fetch:
            if contents is None or self._is_replay:
                '''Try to fetch archive chat data.'''
                self._parser.is_replay = True
                self._fetch_url = "live_chat_replay/get_live_chat_replay?continuation="
                continuation = arcparam.getparam(
                    self._video_id, self.seektime, self._topchat_only)
                livechat_json = (self._get_livechat_json(continuation, client, headers))
                reload_continuation = self._parser.reload_continuation(
                    self._parser.get_contents(livechat_json))
                if reload_continuation:
                    livechat_json = (self._get_livechat_json(
                        reload_continuation, client, headers))
                contents = self._parser.get_contents(livechat_json)
                self._is_replay = True
            self._first_fetch = False
        return contents

    def _get_livechat_json(self, continuation, client, headers):
        '''
        Get json which includes chat data.
        '''
        continuation = urllib.parse.quote(continuation)
        livechat_json = None
        status_code = 0
        url = f"https://www.youtube.com/{self._fetch_url}{continuation}&pbj=1"
        for _ in range(MAX_RETRY + 1):
            with client:
                try:
                    livechat_json = client.get(url, headers=headers).json()
                    break
                except json.JSONDecodeError:
                    time.sleep(1)
                    continue
        else:
            self._logger.error(f"[{self._video_id}]"
                               f"Exceeded retry count. status_code={status_code}")
            raise exceptions.RetryExceedMaxCount()
        return livechat_json

    def _callback_loop(self, callback):
        """ コンストラクタでcallbackを指定している場合、バックグラウンドで
        callbackに指定された関数に一定間隔でチャットデータを投げる。

        Parameter
        ---------
        callback : func
            加工済みのチャットデータを渡す先の関数。
        """
        while self.is_alive():
            items = self._buffer.get()
            processed_chat = self.processor.process(items)
            if isinstance(processed_chat, tuple):
                self._callback(*processed_chat)
            else:
                self._callback(processed_chat)

    def get(self):
        """ bufferからデータを取り出し、processorに投げ、
        加工済みのチャットデータを返す。

        Returns
             : Processorによって加工されたチャットデータ
        """
        if self._callback is None:
            if self.is_alive():
                items = self._buffer.get()
                return self.processor.process(items)
            else:
                return []
        raise exceptions.IllegalFunctionCall(
            "既にcallbackを登録済みのため、get()は実行できません。")

    def is_replay(self):
        return self._is_replay

    def pause(self):
        if self._callback is None:
            return
        if not self._pauser.empty():
            self._pauser.get()

    def resume(self):
        if self._callback is None:
            return
        if self._pauser.empty():
            self._pauser.put_nowait(None)

    def is_alive(self):
        return self._is_alive

    def _finish(self, sender):
        '''Listener終了時のコールバック'''
        try:
            self._task_finished()
        except CancelledError:
            self._logger.debug(f'[{self._video_id}]cancelled:{sender}')

    def terminate(self):
        if self._pauser.empty():
            self._pauser.put_nowait(None)
        self._is_alive = False
        self._buffer.put({})
        self._event.set()
        self.processor.finalize()

    def _task_finished(self):
        '''
        Listenerを終了する。
        '''
        if self.is_alive():
            self.terminate()
        try:
            self.listen_task.result()
        except Exception as e:
            self.exception = e
            if not isinstance(e, exceptions.ChatParseException):
                self._logger.error(f'Internal exception - {type(e)}{str(e)}')
        self._logger.info(f'[{self._video_id}]終了しました')

    def raise_for_status(self):
        if self.exception is not None:
            raise self.exception
