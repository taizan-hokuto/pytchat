from . import asyncdl
from . import duplcheck 
from . import parser
from .. videoinfo import VideoInfo
from ... import config
from ... exceptions import InvalidVideoIdException

logger = config.logger(__name__)
headers=config.headers

class Downloader:
    def __init__(self, video_id, duration, div, callback):
        if not isinstance(div ,int) or div < 1:
            raise ValueError('div must be positive integer.')
        elif div > 10:
            div = 10
        if not isinstance(duration ,int) or duration < 1:
            raise ValueError('duration must be positive integer.')
        self.video_id = video_id
        self.duration = duration
        self.div = div
        self.callback = callback
        self.blocks = []

    def _ready_blocks(self):
        blocks = asyncdl.ready_blocks(
            self.video_id, self.duration, self.div, self.callback)
        self.blocks = [block for block in blocks if block]
        return self  

    def _remove_duplicate_head(self):
        self.blocks = duplcheck.remove_duplicate_head(self.blocks)
        return self

    def _set_block_end(self):
        for i in range(len(self.blocks)-1):
            self.blocks[i].end = self.blocks[i+1].first
        self.blocks[-1].end = self.duration*1000
        self.blocks[-1].is_last =True
        return self

    def _remove_overlap(self):
        self.blocks = duplcheck.remove_overlap(self.blocks)
        return self

    def _download_blocks(self):
        asyncdl.download_patch(self.callback, self.blocks, self.video_id)
        return self

    def _remove_duplicate_tail(self):
        self.blocks = duplcheck.remove_duplicate_tail(self.blocks)
        return self

    def _combine(self):
        ret = []
        for block in self.blocks:
            ret.extend(block.chat_data) 
        return ret

    def download(self):
        return (
            self._ready_blocks()
                ._remove_duplicate_head()
                ._set_block_end()
                ._remove_overlap()
                ._download_blocks()
                ._remove_duplicate_tail()
                ._combine()
        )

def download(video_id, div = 1, callback = None, processor = None):
    duration = 0
    try:
        duration = VideoInfo(video_id).get("duration")
    except InvalidVideoIdException:
        raise
    if duration == 0:
        print("video is live.")
        return []
    data = Downloader(video_id, duration, div, callback).download()
    if processor is None:
        return data
    return processor.process(
        [{'video_id':None,'timeout':1,'chatdata' : (action
        ["replayChatItemAction"]["actions"][0] for action in data)}]
    )

def cancel():
    asyncdl.cancel()