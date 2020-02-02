class Block:
    """Block object represents virtual chunk of chatdata.

    Parameter:
    ---------
    pos : int
        index of this block on block list.

    first : int
        videoOffsetTimeMs of chat_data[0]
        
    last : int
        videoOffsetTimeMs of the last chat_data current read.
        (chat_data[-1])

        this value increases as fetching chatdata progresses.

    temp_last : int
        temporary videoOffsetTimeMs of last chat data,
        equals to first videoOffsetTimeMs of next block.
        when download worker reaches this offset, the download will stop.

    continuation : str
        continuation param of last chat data.

    chat_data : List
    """
    def __init__(self, pos=0, first=0, last=0,
                continuation='', chat_data=[]):
        self.pos = pos
        self.first = first
        self.last = last
        self.temp_last = 0
        self.continuation = continuation
        self.chat_data = chat_data