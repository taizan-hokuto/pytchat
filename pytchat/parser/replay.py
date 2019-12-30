import json
from .. import config
from .. exceptions import ( 
    ResponseContextError, 
    NoContentsException, 
    NoContinuationsException )


logger = config.logger(__name__)

class Parser:
    def parse(self, jsn):
        """
        このparse関数はReplayChat._listen() 関数から定期的に呼び出される。
        引数jsnはYoutubeから取得したアーカイブ済みチャットデータの生JSONであり、
        このparse関数によって与えられたJSONを以下に分割して返す。
         + timeout (次のチャットデータ取得までのインターバル)
         + chat data（チャットデータ本体）
         + continuation （次のチャットデータ取得に必要となるパラメータ）.
        
        ライブ配信のチャットとアーカイブ済み動画のチャットは構造が若干異なっているが、
        ライブチャットと同じデータ形式に変換することにより、
        同じprocessorでライブとリプレイどちらでも利用できるようにしている。

        Parameter
        ----------
        + jsn : dict
            + Youtubeから取得したチャットデータのJSONオブジェクト。
              （pythonの辞書形式に変換済みの状態で渡される）

        Returns
        -------
        + metadata : dict
            + チャットデータに付随するメタデータ。timeout、 動画ID、continuationパラメータで構成される。           
        + chatdata : list[dict]
            + チャットデータ本体のリスト。
        """
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
            if unknown != "playerSeekContinuationData":
                logger.debug(f"Received unknown continuation type:{unknown}")
                metadata = cont.get(unknown)
        actions = contents['liveChatContinuation'].get('actions')
        if actions is None:
            #後続のチャットデータなし
            return {"continuation":None,"timeout":0,"chatdata":[]}
        interval = self.get_interval(actions)
        metadata.setdefault("timeoutMs",interval)
        """アーカイブ済みチャットはライブチャットと構造が異なっているため、以下の行により
        ライブチャットと同じ形式にそろえる"""
        chatdata = [action["replayChatItemAction"]["actions"][0] for action in actions]
        return metadata, chatdata

    def get_interval(self, actions: list):
        if actions is None:
            return 0
        start = int(actions[0]["replayChatItemAction"]["videoOffsetTimeMsec"])
        last = int(actions[-1]["replayChatItemAction"]["videoOffsetTimeMsec"])
        return (last - start)



