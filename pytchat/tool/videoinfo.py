import json 
import re
import requests
from .. import config
from .. import util
from ..exceptions import InvalidVideoIdException 
headers = config.headers
pattern=re.compile(r"yt\.setConfig\({'PLAYER_CONFIG': ({.*})}\);")

class VideoInfo:
    def __init__(self,video_id):
        self.video_id = video_id
        self.info = self._get_info(video_id)

    def _get_info(self,video_id):
        url = f"https://www.youtube.com/embed/{video_id}"
        resp= requests.get(url, headers = headers)
        resp.raise_for_status()
        return  self._parse(resp.text)

    def _parse(self,html):
        result = re.search(pattern, html)
        res= json.loads(result.group(1))
        response = res["args"].get("embedded_player_response")
        if response is None:
            raise InvalidVideoIdException("動画IDが無効です。")
        renderer = (json.loads(response))["embedPreview"]["thumbnailPreviewRenderer"]
        return {
            "duration": int(renderer["videoDurationSeconds"]) if renderer.get("videoDurationSeconds") else 0,
            "title" : [''.join(run["text"]) for run in renderer["title"]["runs"]][0] if renderer.get("title") else None,
            "channelId" : renderer["videoDetails"]["embeddedPlayerOverlayVideoDetailsRenderer"]["channelThumbnailEndpoint"]["channelThumbnailEndpoint"]["urlEndpoint"]["urlEndpoint"]["url"][9:] if renderer.get("videoDetails") else None,
            "authorProfileImage" : renderer["videoDetails"]["embeddedPlayerOverlayVideoDetailsRenderer"]["channelThumbnail"]["thumbnails"][0]["url"] if renderer.get("videoDetails") else None,
            "thumbnail" : renderer["defaultThumbnail"]["thumbnails"][2]["url"] if renderer.get("defaultThumbnail") else None,
            "channelName" : renderer["videoDetails"]["embeddedPlayerOverlayVideoDetailsRenderer"]["expandedRenderer"]["embeddedPlayerOverlayVideoDetailsExpandedRenderer"]["title"]["runs"][0]["text"] if renderer.get("videoDetails") else None,
            "movingThumbnail" : renderer["movingThumbnail"]["thumbnails"][0]["url"] if renderer.get("movingThumbnail") else None
        }

    def get(self,item):
        return self.info.get(item)
    


