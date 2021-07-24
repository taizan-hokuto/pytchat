"""
pytchat is a lightweight python library to browse youtube livechat without Selenium or BeautifulSoup.
"""
__copyright__    = 'Copyright (C) 2019, 2020, 2021 taizan-hokuto'
__version__      = '0.5.5'
__license__      = 'MIT'
__author__       = 'taizan-hokuto'
__author_email__ = '55448286+taizan-hokuto@users.noreply.github.com'
__url__          = 'https://github.com/taizan-hokuto/pytchat'


from .exceptions import (
    ChatParseException,
    ResponseContextError,
    NoContents,
    NoContinuation,
    IllegalFunctionCall,
    InvalidVideoIdException,
    UnknownConnectionError,
    RetryExceedMaxCount,
    ChatDataFinished,
    ReceivedUnknownContinuation,
    FailedExtractContinuation,
    VideoInfoParseError,
    PatternUnmatchError
)

from .api import (
    config,
    LiveChat,
    LiveChatAsync,
    ChatProcessor,
    CompatibleProcessor,
    DummyProcessor,
    DefaultProcessor,
    HTMLArchiver,
    TSVArchiver,
    JsonfileArchiver,
    SimpleDisplayProcessor,
    SpeedCalculator,
    SuperchatCalculator,
    create
)
# flake8: noqa