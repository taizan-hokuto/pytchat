import httpx
import json
import signal
import time
import traceback
import urllib.parse
from ..parser.live import Parser
from .. import config
from .. import exceptions
from ..paramgen import liveparam, arcparam
from ..processors.default.processor import DefaultProcessor
from ..processors.combinator import Combinator
from ..util.extract_video_id import extract_video_id

headers = config.headers
MAX_RETRY = 10


class PytchatCore:
    '''

    Parameter
    ---------
    video_id : str

    seektime : int
        start position of fetching chat (seconds).
        This option is valid for archived chat only.
        If negative value, chat data posted before the start of the broadcast
        will be retrieved as well.

    processor : ChatProcessor

    interruptable : bool
        Allows keyboard interrupts.
        Set this parameter to False if your own threading program causes
        the problem.

    force_replay : bool
        force to fetch archived chat data, even if specified video is live.

    topchat_only : bool
        If True, get only top chat.

    hold_exception : bool [default:True]
        If True, when exceptions occur, the exception is held internally,
        and can be raised by raise_for_status().

    Attributes
    ---------
    _is_alive : bool
        Flag to stop getting chat.
    '''

    _setup_finished = False

    def __init__(self, video_id,
                 seektime=-1,
                 processor=DefaultProcessor(),
                 interruptable=True,
                 force_replay=False,
                 topchat_only=False,
                 hold_exception=True,
                 logger=config.logger(__name__),
                 ):
        self._video_id = extract_video_id(video_id)
        self.seektime = seektime
        if isinstance(processor, tuple):
            self.processor = Combinator(processor)
        else:
            self.processor = processor
        self._is_alive = True
        self._is_replay = force_replay
        self._hold_exception = hold_exception
        self._exception_holder = None
        self._parser = Parser(
            is_replay=self._is_replay,
            exception_holder=self._exception_holder
        )
        self._first_fetch = True
        self._fetch_url = "live_chat/get_live_chat?continuation="
        self._topchat_only = topchat_only
        self._logger = logger
        if interruptable:
            signal.signal(signal.SIGINT, lambda a, b: self.terminate())
        self._setup()

    def _setup(self):
        time.sleep(0.1)  # sleep shortly to prohibit skipping fetching data
        """Fetch first continuation parameter,
        create and start _listen loop.
        """
        self.continuation = liveparam.getparam(self._video_id, 3)

    def _get_chat_component(self):
        
        ''' Fetch chat data and store them into buffer,
        get next continuaiton parameter and loop.

        Parameter
        ---------
        continuation : str
            parameter for next chat data
        '''
        try:
            with httpx.Client(http2=True) as client:
                if self.continuation and self._is_alive:
                    contents = self._get_contents(self.continuation, client, headers)
                    metadata, chatdata = self._parser.parse(contents)
                    timeout = metadata['timeoutMs'] / 1000
                    chat_component = {
                        "video_id": self._video_id,
                        "timeout": timeout,
                        "chatdata": chatdata
                    }
                    self.continuation = metadata.get('continuation')
                    return chat_component
        except exceptions.ChatParseException as e:
            self._logger.debug(f"[{self._video_id}]{str(e)}")
            self._raise_exception(e)
        except (TypeError, json.JSONDecodeError) as e:
            self._logger.error(f"{traceback.format_exc(limit=-1)}")
            self._raise_exception(e)

        self._logger.debug(f"[{self._video_id}]finished fetching chat.")
        self._raise_exception(exceptions.ChatDataFinished)

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
        err = None
        url = f"https://www.youtube.com/{self._fetch_url}{continuation}&pbj=1"
        for _ in range(MAX_RETRY + 1):
            with client:
                try:
                    livechat_json = client.get(url, headers=headers).json()
                    break
                except (json.JSONDecodeError, httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
                    err = e
                    time.sleep(2)
                    continue
        else:
            self._logger.error(f"[{self._video_id}]"
                               f"Exceeded retry count. Last error: {str(err)}")
            self._raise_exception(exceptions.RetryExceedMaxCount())
        return livechat_json
    
    def get(self):
        if self.is_alive():
            chat_component = self._get_chat_component()
            return self.processor.process([chat_component])
        else:
            return []

    def is_replay(self):
        return self._is_replay

    def is_alive(self):
        return self._is_alive

    def terminate(self):
        self._is_alive = False
        self.processor.finalize()

    def raise_for_status(self):
        if self._exception_holder is not None:
            raise self._exception_holder

    def _raise_exception(self, exception: Exception = None):
        self._is_alive = False
        if self._hold_exception is False:
            raise exception
        self._exception_holder = exception
