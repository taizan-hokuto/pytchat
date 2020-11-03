
import queue


class Buffer(queue.Queue):
    '''
    Buffer for storing chat data.

    Parameter
    ---------
    maxsize : int
        Maximum number of chat blocks to be stored.
        If it exceeds the maximum, the oldest chat block will be discarded.
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
