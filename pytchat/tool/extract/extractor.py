from typing import Generator
from . import asyncdl
from . import duplcheck
from .. videoinfo import VideoInfo
from ... import config
from ... exceptions import InvalidVideoIdException
from ... import util

logger = config.logger(__name__)
headers = config.headers


class Extractor:
    def __init__(self, video_id, div=1, callback=None, processor=None):
        if not isinstance(div, int) or div < 1:
            raise ValueError('div must be positive integer.')
        elif div > 10:
            div = 10
        self.video_id = util.extract_video_id(video_id)
        self.div = div
        self.callback = callback
        self.processor = processor
        self.duration = self._get_duration_of_video(video_id)
        self.blocks = []

    def _get_duration_of_video(self, video_id):
        duration = 0
        try:
            duration = VideoInfo(video_id).get_duration()
        except InvalidVideoIdException:
            raise
        return duration

    def _ready_blocks(self):
        blocks = asyncdl.ready_blocks(
            self.video_id, self.duration, self.div, self.callback)
        self.blocks = [block for block in blocks if block]
        return self

    def _remove_duplicate_head(self):
        self.blocks = duplcheck.remove_duplicate_head(self.blocks)
        return self

    def _set_block_end(self):
        if len(self.blocks) > 0:
            for i in range(len(self.blocks) - 1):
                self.blocks[i].end = self.blocks[i + 1].first
            self.blocks[-1].end = self.duration * 1000
            self.blocks[-1].is_last = True
        return self

    def _remove_overlap(self):
        self.blocks = duplcheck.remove_overlap(self.blocks)
        return self

    def _download_blocks(self):
        asyncdl.fetch_patch(self.callback, self.blocks, self.video_id)
        return self

    def _remove_duplicate_tail(self):
        self.blocks = duplcheck.remove_duplicate_tail(self.blocks)
        return self

    def _get_chatdata(self) -> Generator:
        for block in self.blocks:
            for chatdata in block.chat_data:
                yield chatdata

    def _execute_extract_operations(self):
        return (
            self._ready_blocks()
                ._remove_duplicate_head()
                ._set_block_end()
                ._remove_overlap()
                ._download_blocks()
                ._remove_duplicate_tail()
                ._get_chatdata()
        )

    def extract(self):
        if self.duration == 0:
            print("\nCannot extract chat data:\n The specified video has not yet been archived.")
            return []
        data = self._execute_extract_operations()
        if self.processor is None:
            return data
        ret = self.processor.process(
            [{'video_id': None,
              'timeout': 1,
              'chatdata': (action["replayChatItemAction"]["actions"][0] for action in data)}]
        )
        self.processor.finalize()
        return ret

    def cancel(self):
        asyncdl.cancel()
