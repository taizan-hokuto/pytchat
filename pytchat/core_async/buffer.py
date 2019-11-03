
import asyncio
class Buffer(asyncio.Queue):
    '''
    チャットデータを格納するバッファの役割を持つFIFOキュー

    Parameter
    ---------
    maxsize : int
        格納するチャットブロックの最大個数。0の場合は無限。
        最大値を超える場合は古いチャットブロックから破棄される。
    '''
    def __init__(self,maxsize = 0):
        super().__init__(maxsize)
    
    async def put(self,item):
        if item is None:
            return 
        if super().full():
            super().get_nowait()
        await super().put(item)

    async def get(self):
        ret = []
        ret.append(await super().get())
        while not super().empty():
            ret.append(super().get_nowait())
        return ret