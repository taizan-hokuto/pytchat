
import asyncio
import httpx
import json
import signal
import time
import traceback
from asyncio import Queue
from concurrent.futures import CancelledError
from .buffer import Buffer
from ..parser.live import Parser
from .. import config
from .. import exceptions
from .. import util
from ..paramgen import liveparam, arcparam
from ..processors.default.processor import DefaultProcessor
from ..processors.combinator import Combinator

headers = config.headers
MAX_RETRY = 10


class LiveChatAsync:
    '''LiveChatAsync object fetches chat data and stores them
    in a buffer with asyncio.

    Parameter
    ---------
    video_id : str

    seektime : int
        start position of fetching chat (seconds).
        This option is valid for archived chat only.
        If negative value, chat data posted before the start of the broadcast
        will be retrieved as well.

    processor : ChatProcessor

    buffer : Buffer
        buffer of chat data fetched background.

    interruptable : bool
        Allows keyboard interrupts.
        Set this parameter to False if your own threading program causes
        the problem.

    callback : func
        function called periodically from _listen().

    done_callback : func
        function called when listener ends.

    exception_handler : func

    direct_mode : bool
        If True, invoke specified callback function without using buffer.
        callback is required. If not, IllegalFunctionCall will be raised.

    force_replay : bool
        force to fetch archived chat data, even if specified video is live.

    topchat_only : bool
        If True, get only top chat.

    replay_continuation : str
        If this parameter is not None, the processor will attempt to get chat data from continuation.
        This parameter is only allowed in archived mode.

    Attributes
    ---------
    _is_alive : bool
        Flag to stop getting chat.
    '''

    _setup_finished = False

    def __init__(self, video_id,
                 seektime=-1,
                 processor=DefaultProcessor(),
                 buffer=None,
                 client = httpx.AsyncClient(http2=True),
                 interruptable=True,
                 callback=None,
                 done_callback=None,
                 exception_handler=None,
                 direct_mode=False,
                 force_replay=False,
                 topchat_only=False,
                 logger=config.logger(__name__),
                 replay_continuation=None
                 ):
        self._client:httpx.AsyncClient = client
        self._video_id = util.extract_video_id(video_id)
        self.seektime = seektime
        if isinstance(processor, tuple):
            self.processor = Combinator(processor)
        else:
            self.processor = processor
        self._buffer = buffer
        self._callback = callback
        self._done_callback = done_callback
        self._exception_handler = exception_handler
        self._direct_mode = direct_mode
        self._is_alive = True
        self._is_replay = force_replay or (replay_continuation is not None)
        self._parser = Parser(is_replay=self._is_replay)
        self._pauser = Queue()
        self._pauser.put_nowait(None)
        self._first_fetch = replay_continuation is None
        self._fetch_url = config._sml if replay_continuation is None else config._smr
        self._topchat_only = topchat_only
        self._dat = ''
        self._last_offset_ms = 0
        self._logger = logger
        self.exception = None
        self.continuation = replay_continuation
        LiveChatAsync._logger = logger

        if exception_handler:
            self._set_exception_handler(exception_handler)
        if interruptable:
            signal.signal(signal.SIGINT,
                (lambda a, b: self._keyboard_interrupt()))
        self._setup()

    def _setup(self):
        # An exception is raised when direct mode is true and no callback is set.
        if self._direct_mode:
            if self._callback is None:
                raise exceptions.IllegalFunctionCall(
                    "When direct_mode=True, callback parameter is required.")
        else:
            # Create a default buffer if `direct_mode` is False and buffer is not set.
            if self._buffer is None:
                self._buffer = Buffer(maxsize=20)
                # Create a loop task to call callback if the `callback` param is specified.
            if self._callback is None:
                pass
            else:
                # Create a loop task to call callback if the `callback` param is specified.
                loop = asyncio.get_event_loop()
                loop.create_task(self._callback_loop(self._callback))
        # Start a loop task for _listen()
        loop = asyncio.get_event_loop()
        self.listen_task = loop.create_task(self._startlisten())
        # Register add_done_callback
        if self._done_callback is None:
            self.listen_task.add_done_callback(self._finish)
        else:
            self.listen_task.add_done_callback(self._done_callback)

    async def _startlisten(self):
        """Fetch first continuation parameter,
        create and start _listen loop.
        """
        if not self.continuation:
            channel_id = await util.get_channelid_async(self._client, self._video_id)
            self.continuation = liveparam.getparam(
                self._video_id,
                channel_id,
                past_sec=3)

        await self._listen(self.continuation)

    async def _listen(self, continuation):
        ''' Fetch chat data and store them into buffer,
        get next continuaiton parameter and loop.

        Parameter
        ---------
        continuation : str
            parameter for next chat data
        '''
        try:
            async with self._client as client:
                while(continuation and self._is_alive):
                    continuation = await self._check_pause(continuation)
                    contents = await self._get_contents(continuation, client, headers) #Q#
                    metadata, chatdata = self._parser.parse(contents)
                    continuation = metadata.get('continuation')
                    if continuation:
                        self.continuation = continuation
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
                            await self._callback(*processed_chat)
                        else:
                            await self._callback(processed_chat)
                    else:
                        await self._buffer.put(chat_component)
                    diff_time = timeout - (time.time() - time_mark)
                    await asyncio.sleep(diff_time)
                    self._last_offset_ms = metadata.get('last_offset_ms', 0)
        except exceptions.ChatParseException as e:
            self._logger.debug(f"[{self._video_id}]{str(e)}")
            raise
        except Exception:
            self._logger.error(f"{traceback.format_exc(limit=-1)}")
            raise

        self._logger.debug(f"[{self._video_id}] finished fetching chat.")

    async def _check_pause(self, continuation):
        if self._pauser.empty():
            '''pause'''
            await self._pauser.get()
            '''resume:
                prohibit from blocking by putting None into _pauser.
            '''
            self._pauser.put_nowait(None)
            if not self._is_replay:
                async with self._client as client:
                    channel_id = await util.get_channelid_async(client, self.video_id)
                    continuation = liveparam.getparam(self._video_id, 
                                    channel_id,
                                    past_sec=3)
                    
        return continuation

    async def _get_contents(self, continuation, client, headers):
        '''Get 'continuationContents' from livechat json.
           If contents is None at first fetching,
           try to fetch archive chat data.

          Return:
          -------
            'continuationContents' which includes metadata & chatdata.
        '''
        livechat_json = await self._get_livechat_json(continuation, client, replay=self._is_replay, offset_ms=self._last_offset_ms)
        contents, dat = self._parser.get_contents(livechat_json)
        if self._dat == '' and dat:
            self._dat = dat
        if self._first_fetch:
            if contents is None or self._is_replay:
                '''Try to fetch archive chat data.'''
                self._parser.is_replay = True
                self._fetch_url = config._smr
                channelid = await util.get_channelid_async(client, self._video_id)
                continuation = arcparam.getparam(
                    self._video_id, self.seektime, self._topchat_only, channelid)
                livechat_json = (await self._get_livechat_json(
                                 continuation, client, replay=True, offset_ms=self.seektime * 1000))
                reload_continuation = self._parser.reload_continuation(
                    self._parser.get_contents(livechat_json)[0])
                if reload_continuation:
                    livechat_json = (await self._get_livechat_json(
                        reload_continuation, client, headers))
                contents, _ = self._parser.get_contents(livechat_json)
                self._is_replay = True
            self._first_fetch = False
        return contents

    async def _get_livechat_json(self, continuation, client, replay: bool, offset_ms: int = 0):
        '''
        Get json which includes chat data.
        '''
        livechat_json = None
        if offset_ms < 0:
            offset_ms = 0
        param = util.get_param(continuation, dat=self._dat, replay=replay, offsetms=offset_ms)
        for _ in range(MAX_RETRY + 1):
            try:
                resp = await client.post(self._fetch_url, json=param)
                livechat_json = resp.json()
                break
            except (json.JSONDecodeError, httpx.HTTPError):
                await asyncio.sleep(2)
                continue
        else:
            self._logger.error(f"[{self._video_id}]"
                               f"Exceeded retry count.")
            raise exceptions.RetryExceedMaxCount()
        return livechat_json

    async def _callback_loop(self, callback):
        """ If a callback is specified in the constructor,
        it throws chat data at regular intervals to the
        function specified in the callback in the backgroun

        Parameter
        ---------
        callback : func
            function to which the processed chat data is passed.
        """
        while self.is_alive():
            items = await self._buffer.get()
            processed_chat = self.processor.process(items)
            if isinstance(processed_chat, tuple):
                await self._callback(*processed_chat)
            else:
                await self._callback(processed_chat)

    async def get(self):
        """
        Retrieves data from the buffer,
        throws it to the processor,
        and returns the processed chat data.

        Returns
             : Chat data processed by the Processor
        """
        if self._callback is None:
            if self.is_alive():
                items = await self._buffer.get()
                return self.processor.process(items)
            else:
                return []
        raise exceptions.IllegalFunctionCall(
            "Callback parameter is already set, so get() cannot be performed.")

    def is_replay(self):
        return self._is_replay

    def pause(self):
        if self._callback is None:
            return
        if not self._pauser.empty():
            self._pauser.get_nowait()

    def resume(self):
        if self._callback is None:
            return
        if self._pauser.empty():
            self._pauser.put_nowait(None)

    def is_alive(self):
        return self._is_alive

    def _finish(self, sender):
        '''Called when the _listen() task finished.'''
        try:
            self._task_finished()
        except CancelledError:
            self._logger.debug(f'[{self._video_id}] cancelled:{sender}')

    def terminate(self):
        if not self.is_alive():
            return 
        if self._pauser.empty():
            self._pauser.put_nowait(None)
        self._is_alive = False
        self._buffer.put_nowait({})
        self.processor.finalize()

    def _keyboard_interrupt(self):
        self.exception = exceptions.ChatDataFinished()
        self.terminate()

    def _task_finished(self):
        if self.is_alive():
            self.terminate()
        try:
            self.listen_task.result()
        except Exception as e:
            self.exception = e
            if not isinstance(e, exceptions.ChatParseException):
                self._logger.error(f'Internal exception - {type(e)}{str(e)}')
        self._logger.info(f'[{self._video_id}] finished.')

    def raise_for_status(self):
        if self.exception is not None:
            raise self.exception

    @classmethod
    def _set_exception_handler(cls, handler):
        loop = asyncio.get_event_loop()
        loop.set_exception_handler(handler)
