
import queue


class Buffer(queue.Queue):
    '''
    チャットデータを格納するバッファの役割を持つFIFOキュー

    Parameter
    ---------
    max_size : int
        格納するチャットブロックの最大個数。0の場合は無限。
        最大値を超える場合は古いチャットブロックから破棄される。
    '''

    def __init__(self, maxsize=0):
        super().__init__(maxsize=maxsize)

    def put(self, item):
        if item is None:
            return
        if super().full():
            super().get_nowait()
        else:
            super().put(item)

    def put_nowait(self, item):
        if item is None:
            return
        if super().full():
            super().get_nowait()
        else:
            super().put_nowait(item)

    def get(self):
        ret = []
        ret.append(super().get())
        while not super().empty():
            ret.append(super().get())
        return ret
