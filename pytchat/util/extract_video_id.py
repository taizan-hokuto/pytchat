import re
from .. exceptions import InvalidVideoIdException


PATTERN = re.compile(r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)")
YT_VIDEO_ID_LENGTH = 11


def extract_video_id(url_or_id: str) -> str:
    ret = ''
    if type(url_or_id) != str:
        raise TypeError(f"{url_or_id}: URL or VideoID must be str, but {type(url_or_id)} is passed.")
    if len(url_or_id) == YT_VIDEO_ID_LENGTH:
        return url_or_id
    match = re.search(PATTERN, url_or_id)
    if match is None:
        raise InvalidVideoIdException(url_or_id)
    try:
        ret = match.group(4)
    except IndexError:
        raise InvalidVideoIdException(url_or_id)

    if ret is None or len(ret) != YT_VIDEO_ID_LENGTH:
        raise InvalidVideoIdException(url_or_id)
    return ret
