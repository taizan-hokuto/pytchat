import json 
import re
import requests
from .. import config
from .. import util
from ..exceptions import InvalidVideoIdException 
headers = config.headers
pattern=re.compile(r"yt\.setConfig\({'PLAYER_CONFIG': ({.*})}\);")

item_channel_id =[
    "videoDetails",
    "embeddedPlayerOverlayVideoDetailsRenderer",
    "channelThumbnailEndpoint",
    "channelThumbnailEndpoint",
    "urlEndpoint",
    "urlEndpoint",
    "url"
]

item_renderer = [
    "embedPreview",
    "thumbnailPreviewRenderer"
]

item_response = [
    "args",
    "embedded_player_response"
]

item_author_image =[
    "videoDetails",
    "embeddedPlayerOverlayVideoDetailsRenderer",
    "channelThumbnail",
    "thumbnails",
    0,
    "url"
]


item_thumbnail = [
    "defaultThumbnail",
    "thumbnails",
    2,
    "url"
]

item_channel_name = [
    "videoDetails",
    "embeddedPlayerOverlayVideoDetailsRenderer",
    "expandedRenderer",
    "embeddedPlayerOverlayVideoDetailsExpandedRenderer",
    "title",
    "runs",
    0,
    "text"
]

item_moving_thumbnail = [
    "movingThumbnail",
    "thumbnails",
    0,
    "url"
]

class VideoInfo:
    def __init__(self,video_id):
        self.video_id = video_id
        text = self._get_page_text(video_id)
        self._parse(text)
        self._get_attributes()

    def _get_attributes(self):
        self.duration = self._duration()
        self.channel_id = self._channel_id()
        self.channel_name = self._channel_name()
        self.thumbnail = self._thumbnail()
        self.author_image = self._author_image()
        self.title = self._title()
        self.moving_thumbnail = self._moving_thumbnail()

    def _get_page_text(self,video_id):
        url = f"https://www.youtube.com/embed/{video_id}"
        resp= requests.get(url, headers = headers)
        resp.raise_for_status()
        return resp.text

    def _parse(self, text):
        result = re.search(pattern, text)
        res= json.loads(result.group(1))
        response = self._get_item(res, item_response)
        if response is None:
            raise InvalidVideoIdException(
                f"Specified video_id [{self.video_id}] is invalid.")
        self.renderer = self._get_item(json.loads(response), item_renderer)
        if self.renderer is None:
            raise InvalidVideoIdException(
                f"No renderer found in video_id: [{self.video_id}].")

    def _get_item(self, dict_body, items: list):
        for item in items:
            if dict_body is None:
                break
            if isinstance(dict_body, dict):
                dict_body = dict_body.get(item)
                continue
            if isinstance(item, int) and \
               isinstance(dict_body, list) and \
               len(dict_body) > item:
                dict_body = dict_body[item]
                continue
            return None
        return dict_body

    def _duration(self):
        return int(self.renderer.get("videoDurationSeconds") or 0)

    def _title(self):
        if self.renderer.get("title"):
            return [''.join(run["text"]) 
                for run in self.renderer["title"]["runs"]][0]
        return None

    def _channel_id(self):
        channel_url = self._get_item(self.renderer, item_channel_id)
        if channel_url:
            return channel_url[9:]
        return None

    def _author_image(self):
        return self._get_item(self.renderer, item_author_image) 

    def _thumbnail(self):
        return self._get_item(self.renderer, item_thumbnail)

    def _channel_name(self):
        return self._get_item(self.renderer, item_channel_name)
    
    def _moving_thumbnail(self):
        return self._get_item(self.renderer, item_moving_thumbnail)