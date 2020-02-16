class ChatParseException(Exception):
    '''
    チャットデータをパースするライブラリが投げる例外の基底クラス
    '''
    pass

class NoYtinitialdataException(ChatParseException):
    '''
    配信ページ内にチャットデータurlが見つからないときに投げる例外
    '''
    pass

class ResponseContextError(ChatParseException):
    '''
    配信ページでチャットデータ無効の時に投げる例外
    '''
    pass

class NoLivechatRendererException(ChatParseException):
    '''
    チャットデータのJSON中にlivechatRendererがない時に投げる例外
    '''
    pass


class NoContentsException(ChatParseException):
    '''
    チャットデータのJSON中にContinuationContentsがない時に投げる例外
    '''
    pass

class NoContinuationsException(ChatParseException):
    '''
    チャットデータのContinuationContents中にcontinuationがない時に投げる例外
    '''
    pass

class IllegalFunctionCall(Exception):
    '''
    set_callback()を実行済みにもかかわらず
    get()を呼び出した場合の例外
    '''
    pass

class InvalidVideoIdException(Exception):
    pass
