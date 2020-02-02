from . import parser

class DownloadWorker:
    """
    DownloadWorker associates a download session with a block.

    Parameter
    ----------
    fetch :
        download function of asyncdl

    block :
        Block object that includes chat_data
    """
    def __init__(self, fetch, block):
        self.block = block
        self.fetch = fetch
        
    async def run(self, session):
        """Remove extra chats just after ready_blocks(). """
        temp_last = self.block.temp_last
        self.block.chat_data, continuation = self.cut(
            self.block.chat_data, 
            self.block.continuation, 
            self.block.last,
            temp_last )
        """download loop """
        while continuation:
            data, cont, fetched_last = await self.fetch(continuation, session)
            data, continuation = self.cut(data, cont, fetched_last, temp_last)
            self.block.chat_data.extend(data)
        
    def cut(self, data, cont, fetched_last, temp_last):
        """Remove extra chats."""
        if fetched_last < temp_last or temp_last == -1:
            return data, cont
        for i, line in enumerate(data):
            line_offset = parser.get_offset(line)
            if line_offset >= temp_last:
                self.block.last = line_offset
                return data[:i], None