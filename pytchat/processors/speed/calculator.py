"""
speed_calculator.py
チャットの勢いを算出するChatProcessor
Calculate speed of chat.
"""
import time
from .. chat_processor import ChatProcessor


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
            self.last_pos = len(self.items) - 1
            if self.last_pos == self.capacity - 1:
                self.mergin = False
            return
        self.last_pos += 1
        if self.last_pos > self.capacity - 1:
            self.last_pos = 0
        self.items[self.last_pos] = item

        self.first_pos += 1
        if self.first_pos > self.capacity - 1:
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
    Calculate the momentum of the chat.

    Divide the difference between the time of the first chat and 
    the time of the last chat in the chat data over a period of 
    time by the number of chats and convert it to speed per minute.

    Parameter
    ----------
    capacity : int
        Maximum number of data for calculating chat momentum 
        to be stored in RingQueue.
    """

    def __init__(self, capacity=10):
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
        Calculates the chat speed based on the data list for calculating
        the chat momentum in RingQueue.

        Return
        ---------------------------
            Chat speed (number of chats converted per minute)
        """
        try:
            # Total number of chats in the queue
            total = sum(item['chat_count'] for item in self.items)
            # Interval between the first and last chats in the queue
            duration = (self.items[self.last_pos]['endtime'] - self.items[self.first_pos]['starttime'])
            if duration != 0:
                return int(total * 60 / duration)
            return 0
        except IndexError:
            return 0

    def _put_chatdata(self, actions):
        """
        Parameter
        ---------
        actions : List[dict]
            List of addChatItemActions
        """
        def _put_emptydata():
            timestamp_now = int(time.time())
            self.put({
                'chat_count': 0,
                'starttime': int(timestamp_now),
                'endtime': int(timestamp_now)
            })

        def _get_timestamp(action: dict):
            try:
                item = action['addChatItemAction']['item']
                timestamp = int(item[list(item.keys())[0]]['timestampUsec'])
            except (KeyError, TypeError):
                return None
            return timestamp

        if actions is None or len(actions) == 0:
            _put_emptydata()
            return

        counter = 0
        starttime = None
        endtime = None

        for action in actions:
            # Get timestampUsec from chatdata
            gettime = _get_timestamp(action)

            if gettime is None:
                continue

            if starttime is None:
                starttime = gettime

            endtime = gettime

            counter += 1

        if starttime is None or endtime is None:
            _put_emptydata()
            return

        self.put({
            'chat_count': counter,
            'starttime': int(starttime / 1000000),
            'endtime': int(endtime / 1000000)
        })
