from .pytchat import PytchatCore
from .. util.extract_video_id import extract_video_id


def create(video_id: str, **kwargs):
    _vid = extract_video_id(video_id)
    return PytchatCore(_vid, **kwargs)
