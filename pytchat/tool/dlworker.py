from . import parser

class DownloadWorker:
    def __init__(self, dl, block, blocklist):
        self.block  = block
        self.blocklist = blocklist
        self.dl = dl

    async def run(self,session):
        temp_last = self.block.temp_last
        self.block.chat_data, continuation = self.cut(
            self.block.chat_data, 
            self.block.continuation, 
            self.block.last,
            temp_last )
        while continuation:
            data, cont, fetched_last = await self.dl(continuation, session)
            data, continuation = self.cut(data, cont, fetched_last, temp_last)
            self.block.chat_data.extend(data)
        
    def cut(self, data, cont, fetched_last, temp_last):
        if fetched_last < temp_last or temp_last == -1:
            return data, cont
        for i, line in enumerate(data):
            line_offset = parser.get_offset(line)
            if line_offset >= temp_last:
                self.block.last = line_offset
                return data[:i], None