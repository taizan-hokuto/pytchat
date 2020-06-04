class Block:
    """Block object represents something like a box
    to join chunk of chatdata.

    Parameter:
    ---------
    first : int :
        videoOffsetTimeMs of the first chat_data
        (chat_data[0])

    last : int :
        videoOffsetTimeMs of the last chat_data.
        (chat_data[-1])

        this value increases as fetching chatdata progresses.

    end : int :
        target videoOffsetTimeMs of last chat data for extract,
        equals to first videoOffsetTimeMs of next block.
        when extract worker reaches this offset, stop fetching.

    continuation : str :
        continuation param of last chat data.

    chat_data : list

    done : bool :
        whether this block has been fetched.

    remaining : int :
        remaining data to extract.
        equals end - last.

    is_last : bool :
        whether this block is the last one in blocklist.

    during_split : bool :
        whether this block is in the process of during_split.
        while True, this block is excluded from duplicate split procedure.
    """

    __slots__ = ['first', 'last', 'end', 'continuation', 'chat_data', 'remaining',
                 'done', 'is_last', 'during_split']

    def __init__(self, first=0, last=0, end=0,
                 continuation='', chat_data=[], is_last=False,
                 during_split=False):
        self.first = first
        self.last = last
        self.end = end
        self.continuation = continuation
        self.chat_data = chat_data
        self.done = False
        self.remaining = self.end - self.last
        self.is_last = is_last
        self.during_split = during_split
