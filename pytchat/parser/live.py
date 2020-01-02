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
    NoContinuationsException )


logger = config.logger(__name__)

from .. import util
class Parser:

    def __init__(self):
        self.mode = 'LIVE'

    def get_contents(self, jsn):
        if jsn is None: 
            return {'timeoutMs':0,'continuation':None},[]
        if jsn['response']['responseContext'].get('errors'):
            raise ResponseContextError('The video_id would be wrong, or video is deleted or private.')
        contents=jsn['response'].get('continuationContents')
        return contents

    def parse(self, contents):
        util.save(json.dumps(contents,ensure_ascii=False,indent=2),"v:\\~\\test_",".json")
        """
        このparse関数はLiveChat._listen() 関数から定期的に呼び出される。
        引数jsnはYoutubeから取得したチャットデータの生JSONであり、
        このparse関数によって与えられたJSONを以下に分割して返す。
         + timeout (次のチャットデータ取得までのインターバル)
         + chat data（チャットデータ本体）
         + continuation （次のチャットデータ取得に必要となるパラメータ）.

        Parameter
        ----------
        + contents : dict
            + Youtubeから取得したチャットデータのJSONオブジェクト。
              （pythonの辞書形式に変換済みの状態で渡される）

        Returns
        -------
        + metadata : dict
            + チャットデータに付随するメタデータ。timeout、 動画ID、continuationパラメータで構成される。           
        + chatdata : list[dict]
            + チャットデータ本体のリスト。
        """
        # if jsn is None: 
        #     return {'timeoutMs':0,'continuation':None},[]
        # if jsn['response']['responseContext'].get('errors'):
        #     raise ResponseContextError('動画に接続できません。'
        # '動画IDが間違っているか、動画が削除／非公開の可能性があります。')
        # contents=jsn['response'].get('continuationContents')
        '''配信が終了した場合、もしくはチャットデータが取得できない場合'''
        if contents is None:
            raise NoContentsException('チャットデータを取得できませんでした。')

        cont = contents['liveChatContinuation']['continuations'][0]
        if cont is None:
            raise NoContinuationsException('No Continuation')
        metadata = (cont.get('invalidationContinuationData')  or
                    cont.get('timedContinuationData')         or
                    cont.get('reloadContinuationData')
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