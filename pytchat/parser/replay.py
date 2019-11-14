import json
from .. import config
from .. import mylogger
from .. exceptions import ( 
    ResponseContextError, 
    NoContentsException, 
    NoContinuationsException )


logger = mylogger.get_logger(__name__,mode=config.LOGGER_MODE)


class Parser:
    def parse(self, jsn):
        if jsn is None: 
            return {'timeoutMs':0,'continuation':None},[]
        if jsn['response']['responseContext'].get('errors'):
            raise ResponseContextError('動画に接続できません。'
        '動画IDが間違っているか、動画が削除／非公開の可能性があります。')
        contents=jsn['response'].get('continuationContents')
        #配信が終了した場合、もしくはチャットデータが取得できない場合
        if contents is None:
            raise NoContentsException('チャットデータを取得できませんでした。')

        cont = contents['liveChatContinuation']['continuations'][0]
        if cont is None:
            raise NoContinuationsException('Continuationがありません。')
        metadata = cont.get('liveChatReplayContinuationData')
        if metadata is None:
            unknown = list(cont.keys())[0]
            if unknown:
                metadata = cont.get(unknown)
        
        actions = contents['liveChatContinuation'].get('actions')
        if actions is None:
            raise NoContentsException('チャットデータを取得できませんでした。')
        interval = self.get_interval(actions)
        metadata.setdefault("timeoutMs",interval)
        chatdata = []
        for action in actions:
            chatdata.append(action["replayChatItemAction"]["actions"][0])
        return metadata, chatdata

    def get_interval(self, actions: list):
        if actions is None:
            return 0
        start = int(actions[0]["replayChatItemAction"]["videoOffsetTimeMsec"])
        last = int(actions[-1]["replayChatItemAction"]["videoOffsetTimeMsec"])
        return (last - start)



