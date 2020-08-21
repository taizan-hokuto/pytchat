class InvalidVideoIdException(Exception):
    '''
    Thrown when the video_id is not exist (VideoInfo).
    '''
    pass


class UnknownConnectionError(Exception):
    pass


class VideoInfoParseException(Exception):
    '''
    thrown when failed to parse video info
    '''