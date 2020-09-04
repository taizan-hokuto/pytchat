class InvalidVideoIdException(Exception):
    '''
    Thrown when the video_id is not exist (VideoInfo).
    '''
    pass


class UnknownConnectionError(Exception):
    pass


class VideoInfoParseError(Exception):
    '''
    thrown when failed to parse video info
    '''


class PatternUnmatchError(VideoInfoParseError):
    '''
    thrown when failed to parse video info with unmatched pattern
    '''
    def __init__(self, doc):
        self.msg = "PatternUnmatchError"
        self.doc = doc
