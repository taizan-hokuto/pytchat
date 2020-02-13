from . import asyncdl
from . import parser
from . duplcheck import duplicate_head, duplicate_tail, overwrap
from . videoinfo import VideoInfo
from .. import config
from .. exceptions import InvalidVideoIdException

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

    def ready_blocks(self):
        result = asyncdl.ready_blocks(
            self.video_id, self.duration, self.div, self.callback)
        self.blocks = [block for block in result if block]
        return self  

    def remove_duplicate_head(self):
        self.blocks = duplicate_head(self.blocks)
        return self

    def set_temporary_last(self):
        for i in range(len(self.blocks)-1):
            self.blocks[i].end = self.blocks[i+1].first
        self.blocks[-1].end = self.duration*1000
        self.blocks[-1].is_last =True
        return self

    def remove_overwrap(self):
        self.blocks = overwrap(self.blocks)
        return self

    def download_blocks(self):
        asyncdl.download_chunk(self.callback, self.blocks, self.video_id)
        return self

    def remove_duplicate_tail(self):
        self.blocks = duplicate_tail(self.blocks)
        return self

    def combine(self):
        ret = []
        for block in self.blocks:
            ret.extend(block.chat_data) 
        return ret

    def download(self):
        return (
            self.ready_blocks()
                .remove_duplicate_head()
                .remove_overwrap()
                .set_temporary_last()
                .download_blocks()
                .remove_duplicate_tail()
                .combine()
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
        [{'video_id':None,'timeout':1,'chatdata' : [action
        ["replayChatItemAction"]["actions"][0] for action in data]}]
    )

def cancel():
    asyncdl.cancel()
