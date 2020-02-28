from . import asyncdl
from . import parser
from .. videoinfo import VideoInfo
from ... import config
from ... exceptions import InvalidVideoIdException
logger = config.logger(__name__)
headers=config.headers

class SuperChatMiner:
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
        self.blocks = [block for block in blocks if block is not None]
        return self  

    def _set_block_end(self):
        for i in range(len(self.blocks)-1):
            self.blocks[i].end = self.blocks[i+1].first
        self.blocks[-1].end = self.duration
        self.blocks[-1].is_last =True
        return self

    def _download_blocks(self):
        asyncdl.fetch_patch(self.callback, self.blocks, self.video_id)
        return self

    def _combine(self):
        ret = []
        for block in self.blocks:
            ret.extend(block.chat_data) 
        return ret

    def extract(self):
        return (
            self._ready_blocks()
                ._set_block_end()
                ._download_blocks()
                ._combine()
        )

def extract(video_id, div = 1, callback = None, processor = None):
    duration = 0
    try:
        duration = VideoInfo(video_id).get_duration()
    except InvalidVideoIdException:
        raise
    if duration == 0:
        print("video is live.")
        return []
    data = SuperChatMiner(video_id, duration, div, callback).extract()
    if processor is None:
        return data
    return processor.process(
        [{'video_id':None,'timeout':1,'chatdata' : (action
        for action in data)}]
    )

def cancel():
    asyncdl.cancel()