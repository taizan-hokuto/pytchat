import httpx
import json
import re
import time
from .. import config
from ..exceptions import InvalidVideoIdException, PatternUnmatchError, UnknownConnectionError
from ..util import extract_video_id


headers = config.headers
pattern = re.compile(r"['\"]PLAYER_CONFIG['\"]:\s*({.*})")
pattern2 = re.compile(r"yt\.setConfig\((\{[\s\S]*?\})\);")

item_channel_id = [
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

item_response2 = [
    "PLAYER_VARS",
    "embedded_player_response"
]
item_author_image = [
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
    '''
    VideoInfo object retrieves YouTube video information.

    Parameter
    ---------
    video_id : str

    Exception
    ---------
    InvalidVideoIdException :
        Occurs when video_id does not exist on YouTube.
    '''

    def __init__(self, video_id):
        self.video_id = extract_video_id(video_id)
        self.client = httpx.Client(http2=True)
        self.new_pattern_text = False
        err = None
        for _ in range(3):
            try:
                text = self._get_page_text(self.video_id)
                self._parse(text)
                break
            except (InvalidVideoIdException, UnknownConnectionError) as e:
                raise e
            except Exception as e:
                err = e
                time.sleep(2)
                pass
        else:
            raise err

    def _get_page_text(self, video_id):
        url = f"https://www.youtube.com/embed/{video_id}"
        err = None
        for _ in range(3):
            try:
                resp = self.client.get(url, headers=headers)
                resp.raise_for_status()
                break
            except httpx.HTTPError as e:
                err = e
                time.sleep(3)
        else:
            raise UnknownConnectionError(str(err))

        return resp.text

    def _parse(self, text):
        result = re.search(pattern, text)
        if result is None:
            result = re.search(pattern2, text)
            if result is None:
                raise PatternUnmatchError(doc=text)
            else:
                self.new_pattern_text = True
        decoder = json.JSONDecoder()
        if self.new_pattern_text:
            res = decoder.raw_decode(result.group(1))[0]
        else:
            res = decoder.raw_decode(result.group(1)[:-1])[0]
        if self.new_pattern_text:
            response = self._get_item(res, item_response2)
        else:
            response = self._get_item(res, item_response)
        if response is None:
            if self.new_pattern_text:
                self._check_video_is_private(res.get("PLAYER_VARS"))
            else:
                self._check_video_is_private(res.get("args"))
        self._renderer = self._get_item(json.loads(response), item_renderer)
        if self._renderer is None:
            raise InvalidVideoIdException(
                f"No renderer found in video_id: [{self.video_id}].")

    def _check_video_is_private(self, args):
        if args and args.get("video_id"):
            raise InvalidVideoIdException(
                f"video_id [{self.video_id}] is private or deleted.")
        raise InvalidVideoIdException(
            f"video_id [{self.video_id}] is invalid.")

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

    def get_duration(self):
        duration_seconds = self._renderer.get("videoDurationSeconds")
        if duration_seconds:
            '''Fetched value is string, so cast to integer.'''
            return int(duration_seconds)
        '''When key is not found, explicitly returns None.'''
        return None

    def get_title(self):
        if self._renderer.get("title"):
            return [''.join(run["text"])
                    for run in self._renderer["title"]["runs"]][0]
        return None

    def get_channel_id(self):
        channel_url = self._get_item(self._renderer, item_channel_id)
        if channel_url:
            return channel_url[9:]
        return None

    def get_author_image(self):
        return self._get_item(self._renderer, item_author_image)

    def get_thumbnail(self):
        return self._get_item(self._renderer, item_thumbnail)

    def get_channel_name(self):
        return self._get_item(self._renderer, item_channel_name)

    def get_moving_thumbnail(self):
        return self._get_item(self._renderer, item_moving_thumbnail)
