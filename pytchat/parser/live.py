"""
pytchat.parser.live
~~~~~~~~~~~~~~~~~~~
This module is parser of live chat JSON.
"""

import json
from .. import config
from .. exceptions import ( 
    ResponseContextError, 
    NoContentsException, 
    NoContinuationsException,
    ChatParseException )


logger = config.logger(__name__)

from .. import util
class Parser:

    def __init__(self):
        self.mode = 'LIVE'

    def get_contents(self, jsn):
        if jsn is None: 
            raise ChatParseException('Called with none JSON object.')
        if jsn['response']['responseContext'].get('errors'):
            raise ResponseContextError('The video_id would be wrong, or video is deleted or private.')
        contents=jsn['response'].get('continuationContents')
        return contents

    def parse(self, contents):
        """
        このparse関数はLiveChat._listen() 関数から定期的に呼び出される。
        引数contentsはYoutubeから取得したチャットデータの生JSONであり、
        与えられたJSONをチャットデータとメタデータに分割して返す。

        Parameter
        ----------
        + contents : dict
            + Youtubeから取得したチャットデータのJSONオブジェクト。
              （pythonの辞書形式に変換済みの状態で渡される）

        Returns
        -------
        tuple:
        + metadata : dict　 チャットデータに付随するメタデータ
         + timeout
         + video_id
         + continuation           
        + chatdata : list[dict]
        　　　 チャットデータ本体のリスト。
        """

        if contents is None:
            '''配信が終了した場合、もしくはチャットデータが取得できない場合'''
            raise NoContentsException('Chat data stream is empty.')

        cont = contents['liveChatContinuation']['continuations'][0]
        if cont is None:
            raise NoContinuationsException('No Continuation')
        metadata = (cont.get('invalidationContinuationData')  or
                    cont.get('timedContinuationData')         or
                    cont.get('reloadContinuationData')        or
                    cont.get('liveChatReplayContinuationData')
                    )
        if metadata is None:
            unknown = list(cont.keys())[0]
            if unknown:
                logger.debug(f"Received unknown continuation type:{unknown}")
                metadata = cont.get(unknown)
        return self._create_data(metadata, contents)

    def _create_data(self, metadata, contents):    
        chatdata = contents['liveChatContinuation'].get('actions')
        if self.mode == 'LIVE':    
            metadata.setdefault('timeoutMs', 10000)
        else:
            interval = self._get_interval(chatdata)
            metadata.setdefault("timeoutMs",interval)
            """アーカイブ済みチャットはライブチャットと構造が異なっているため、以下の行により
            ライブチャットと同じ形式にそろえる"""
            chatdata = [action["replayChatItemAction"]["actions"][0] for action in chatdata]
        return metadata, chatdata

    def _get_interval(self, actions: list):
        if actions is None:
            return 0
        start = int(actions[0]["replayChatItemAction"]["videoOffsetTimeMsec"])
        last = int(actions[-1]["replayChatItemAction"]["videoOffsetTimeMsec"])
        return (last - start)