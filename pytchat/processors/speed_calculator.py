"""
speedmeter.py
チャットの勢いを算出するChatProcessor
Calculate speed of chat.
"""
import calendar, datetime, pytz

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

    def __init__(self, capacity = 10):    
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
        
class SpeedCalculator(RingQueue):
    """
    チャットの勢いを計算するクラス
    Parameter
    ----------
        格納するチャットブロックの数
    """

    def __init__(self, capacity, video_id):
        super().__init__(capacity)
        self.video_id=video_id
        self.speed = 0

    def process(self, chat_components: list):
        if chat_components:
            for component in chat_components:
                
                chatdata = component.get('chatdata')
             
                if chatdata is None:
                    return self.speed
                self.speed = self.calc(chatdata)
                return self.speed

    def _value(self):
        
        """
        ActionsQueue内のチャットデータリストから、
        チャット速度を計算して返す

        Return
        ---------------------------
        チャット速度（１分間で換算したチャット数）
        """
        try:        
            #キュー内のactionsの総チャット数
            total = sum(item['chat_count'] for item in self.items)
            #キュー内の最初と最後のチャットの時間差
            duration = (self.items[self.last_pos]['endtime'] 
                        - self.items[self.first_pos]['starttime'])
            if duration != 0:
                return int(total*60/duration)
            return 0
        except IndexError:
            return 0

    def _get_timestamp(self, action :dict):
        """
        チャットデータのtimestampUsecを読み取る
        liveChatTickerSponsorItemRenderer等のtickerデータは時刻格納位置が
        異なるため、時刻データなしとして扱う
        """
        try:
            item = action['addChatItemAction']['item']
            timestamp = int(item[list(item.keys())[0]]['timestampUsec'])
        except (KeyError,TypeError):
            return None
        return timestamp

    def calc(self,actions):

        def empty_data():
            '''
            データがない場合にゼロのデータをリングキューに入れる
            '''
            timestamp_now =  calendar.timegm(datetime.datetime.
            now(pytz.utc).utctimetuple())
            self.put({
                'chat_count':0,
                'starttime':int(timestamp_now),
                'endtime':int(timestamp_now)
            })
            return self._value()

        if actions is None or len(actions)==0:
            return empty_data
           
        #actions内の時刻データを持つチャットデータの数（tickerは除く）
        counter=0        
        #actions内の最初のチャットデータの時刻
        starttime= None
        #actions内の最後のチャットデータの時刻
        endtime=None
        
        for action in actions:
            #チャットデータからtimestampUsecを読み取る
            gettime = self._get_timestamp(action)
            
            #時刻のないデータだった場合は次の行のデータで読み取り試行
            if gettime is None:
                continue
            
            #最初に有効な時刻を持つデータのtimestampをstarttimeに設定
            if starttime is None:
                starttime = gettime
        
            #最後のtimestampを設定(途中で時刻のないデータの場合もあるので上書きしていく)
            endtime = gettime
        
            #チャットの数をインクリメント
            counter+=1

        #チャット速度用のデータをリングキューに送る
        if starttime is None or endtime is None:
            return empty_data
            
        self.put({
            'chat_count':counter,
            'starttime':int(starttime/1000000),
            'endtime':int(endtime/1000000)
        })

        return self._value()
