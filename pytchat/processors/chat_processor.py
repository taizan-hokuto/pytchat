class ChatProcessor:
    '''
     Listenerからチャットデータ（actions）を受け取り
    チャットデータを加工するクラスの抽象クラス
    '''
    def process(self, chat_components: list):
        '''
        チャットデータの加工を表すインターフェース。
        LiveChatオブジェクトから呼び出される。 
               
        Parameter
        ----------
        chat_components: List[component]
            component : dict {
                "video_id" : str
                    動画ID
                "timeout"  : int
                    次のチャットの再読み込みまでの時間(秒）
                "chatdata" : List[dict]
                    チャットデータのリスト
            }
        '''
        pass





