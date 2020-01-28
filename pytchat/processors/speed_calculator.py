"""
speed_calculator.py
チャットの勢いを算出するChatProcessor
Calculate speed of chat.
"""
import time
from .chat_processor import ChatProcessor
class RingQueue:
    """
    リング型キュー
    
    Attributes
    ----------
    items : list
        格納されているアイテムのリスト。
    first_pos : int
        キュー内の一番古いアイテムを示すリストのインデックス。
    last_pos : int
        キュー内の一番新しいアイテムを示すリストのインデックス。
    mergin : boolean
        キュー内に余裕があるか。キュー内のアイテム個数が、キューの最大個数未満であればTrue。
    """

    def __init__(self, capacity):    
        """
        コンストラクタ
        
        Parameter
        ----------
            capacity:このキューに格納するアイテムの最大個数。
                     格納時に最大個数を超える場合は一番古いアイテムから
                     上書きする。
        """
        if capacity <= 0:
            raise ValueError
        self.items = list()
        self.capacity = capacity
        self.first_pos = 0
        self.last_pos = 0
        self.mergin = True

    def put(self, item):
        """
        引数itemに指定されたアイテムをこのキューに格納する。
        キューの最大個数を超える場合は、一番古いアイテムの位置に上書きする。

        Parameter
        ----------
            item:格納するアイテム
        """
        if self.mergin:
            self.items.append(item)
            self.last_pos = len(self.items)-1
            if self.last_pos == self.capacity-1:
                self.mergin = False
            return
        self.last_pos += 1
        if self.last_pos > self.capacity-1:
            self.last_pos = 0
        self.items[self.last_pos] = item
        
        self.first_pos += 1
        if self.first_pos > self.capacity-1:
            self.first_pos = 0

    def get(self):
        """
        キュー内の一番古いアイテムへの参照を返す
        （アイテムは削除しない）

        Return
        ----------
            キュー内の一番古いアイテムへの参照
        """
        return self.items[self.first_pos]

    def item_count(self):
        return len(self.items)
        
class SpeedCalculator(ChatProcessor, RingQueue):
    """
    チャットの勢いを計算する。
    
    一定期間のチャットデータのうち、最初のチャットの投稿時刻と
    最後のチャットの投稿時刻の差を、チャット数で割り返し
    1分あたりの速度に換算する。

    Parameter
    ----------
    capacity : int
        RingQueueに格納するチャット勢い算出用データの最大数
    """

    def __init__(self, capacity = 10):
        super().__init__(capacity)
        self.speed = 0

    def process(self, chat_components: list):
        chatdata = []
        if chat_components:
            for component in chat_components:
                if component.get("chatdata"):
                    chatdata.extend(component.get("chatdata"))

            self._put_chatdata(chatdata)
            self.speed = self._calc_speed()
        return self.speed
                

    def _calc_speed(self):
        """
        RingQueue内のチャット勢い算出用データリストを元に、
        チャット速度を計算して返す

        Return
        ---------------------------
            チャット速度（１分間で換算したチャット数）
        """
        try:        
            #キュー内の総チャット数
            total = sum(item['chat_count'] for item in self.items)
            #キュー内の最初と最後のチャットの時間差
            duration = (self.items[self.last_pos]['endtime'] 
                        - self.items[self.first_pos]['starttime'])
            if duration != 0:
                return int(total*60/duration)
            return 0
        except IndexError:
            return 0

    def _put_chatdata(self, actions):
        """
        チャットデータからタイムスタンプを読み取り、勢い測定用のデータを組み立て、
        RingQueueに投入する。
        200円以上のスパチャはtickerとmessageの2つのデータが生成されるが、
        tickerの方は時刻データの場所が異なることを利用し、勢いの集計から除外している。
        Parameter
        ---------
        actions : List[dict]
            チャットデータ(addChatItemAction) のリスト
        """
        def _put_emptydata():
            '''
            チャットデータがない場合に空のデータをキューに投入する。
            '''
            timestamp_now =  int(time.time())
            self.put({
                'chat_count':0,
                'starttime':int(timestamp_now),
                'endtime':int(timestamp_now)
            })

        def _get_timestamp(action :dict):
            """
            チャットデータから時刻データを取り出す。
            """
            try:
                item = action['addChatItemAction']['item']
                timestamp = int(item[list(item.keys())[0]]['timestampUsec'])
            except (KeyError,TypeError):
                return None
            return timestamp

        if actions is None or len(actions)==0:
            _put_emptydata()
            return 
           
        #actions内の時刻データを持つチャットデータの数
        counter=0        
        #actions内の最初のチャットデータの時刻
        starttime= None
        #actions内の最後のチャットデータの時刻
        endtime=None
        
        for action in actions:
            #チャットデータからtimestampUsecを読み取る
            gettime = _get_timestamp(action)
            
            #時刻のないデータだった場合は次の行のデータで読み取り試行
            if gettime is None:
                continue
            
            #最初に有効な時刻を持つデータのtimestampをstarttimeに設定
            if starttime is None:
                starttime = gettime
        
            #最後のtimestampを設定(途中で時刻のないデータの場合もあるので上書きしていく)
            endtime = gettime
        
            #チャットの数をインクリメント
            counter += 1

        #チャット速度用のデータをRingQueueに送る
        if starttime is None or endtime is None:
            _put_emptydata()
            return 
            
        self.put({
            'chat_count':counter,
            'starttime':int(starttime/1000000),
            'endtime':int(endtime/1000000)
        })

