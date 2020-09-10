"""
pytchat is a lightweight python library to browse youtube livechat without Selenium or BeautifulSoup.
"""
__copyright__    = 'Copyright (C) 2019 taizan-hokuto'
__version__      = '0.2.2'
__license__      = 'MIT'
__author__       = 'taizan-hokuto'
__author_email__ = '55448286+taizan-hokuto@users.noreply.github.com'
__url__          = 'https://github.com/taizan-hokuto/pytchat'

__all__ = ["core_async","core_multithread","processors"]

from .api import (
    cli,
    config,
    LiveChat,
    LiveChatAsync,
    ChatProcessor,
    CompatibleProcessor,
    DummyProcessor,
    DefaultProcessor,
    Extractor, 
    HTMLArchiver,
    TSVArchiver,
    JsonfileArchiver,
    SimpleDisplayProcessor,
    SpeedCalculator,
    SuperchatCalculator,
    VideoInfo
)

# flake8: noqa