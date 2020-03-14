class ChatParseException(Exception):
    '''
    Base exception thrown by the parser
    '''
    pass

class NoYtinitialdataException(ChatParseException):
    '''
    Thrown when the video is not found.
    '''
    pass

class ResponseContextError(ChatParseException):
    '''
    Thrown when chat data is invalid.
    '''
    pass

class NoLivechatRendererException(ChatParseException):
    '''
    Thrown when livechatRenderer is missing in JSON.
    '''
    pass


class NoContentsException(ChatParseException):
    '''
    Thrown when ContinuationContents is missing in JSON.
    '''
    pass

class NoContinuationsException(ChatParseException):
    '''
    Thrown when continuation is missing in ContinuationContents.
    '''
    pass

class IllegalFunctionCall(Exception):
    '''
    Thrown when get () is called even though 
    set_callback () has been executed.
    '''
    pass

class InvalidVideoIdException(Exception):
    '''
    Thrown when the video_id is not exist (VideoInfo).
    '''
    pass

class UnknownConnectionError(Exception):
    pass