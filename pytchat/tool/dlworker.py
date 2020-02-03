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
        continuation = self.block.start()
        """download loop """
        while continuation:
            chats, new_cont, fetched_last = await self.fetch(continuation, session)
            continuation = self.block.fill(chats, new_cont, fetched_last )
            
        
