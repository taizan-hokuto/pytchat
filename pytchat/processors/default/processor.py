from . import parser
import asyncio
import time


class Chatdata:
    def __init__(self,chatlist:list, timeout:float):
        self.items = chatlist
        self.interval = timeout
    
    def tick(self):
        if self.interval == 0:
            time.sleep(3)
            return
        time.sleep(self.interval/len(self.items))

    async def tick_async(self):
        if self.interval == 0:
            await asyncio.sleep(3)
            return
        await asyncio.sleep(self.interval/len(self.items))

class DefaultProcessor:
    def process(self, chat_components: list):

        chatlist = []
        timeout = 0

        if chat_components:
            for component in chat_components:
                timeout += component.get('timeout', 0)
                chatdata = component.get('chatdata')
             
                if chatdata is None: continue
                for action in chatdata:
                    if action is None: continue
                    if action.get('addChatItemAction') is None: continue
                    if action['addChatItemAction'].get('item') is None: continue

                    chat = parser.parse(action)
                    if chat:
                        chatlist.append(chat)
        return Chatdata(chatlist, float(timeout))
  
