from . import parser
class Block:
    """Block object represents virtual chunk of chatdata.

    Parameter:
    ---------
    pos : int :
        index of this block on block list.

    first : int :
        videoOffsetTimeMs of the first chat_data 
        (chat_data[0])
        
    last : int :
        videoOffsetTimeMs of the last chat_data.
        (chat_data[-1])

        this value increases as fetching chatdata progresses.

    temp_last : int :
        target videoOffsetTimeMs of last chat data for download,
        equals to first videoOffsetTimeMs of next block.
        when download worker reaches this offset, stop downloading.

    continuation : str :
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
    
    def start(self):
        chats, cont = self._cut(self.chat_data, self.continuation, self.last)
        self.chat_data = chats
        return cont

    def fill(self, chats, cont, fetched_last):
        chats, cont = self._cut(chats, cont, fetched_last)
        self.chat_data.extend(chats)
        return cont

    def _cut(self, chats, cont, fetched_last):
        if fetched_last < self.temp_last or self.temp_last == -1:
            return chats, cont
        for i, line in enumerate(chats):
            line_offset = parser.get_offset(line)
            if line_offset >= self.temp_last:
                self.last = line_offset
                return chats[:i], None
