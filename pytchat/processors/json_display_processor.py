import json
from .chat_processor import ChatProcessor

class JsonDisplayProcessor(ChatProcessor):

    def process(self,chat_components: list):
        if chat_components:
            for component in chat_components:
                chatdata = component.get('chatdata')
                if chatdata:
                    for chat in chatdata:
                        print(json.dumps(chat,ensure_ascii=False)[:200])

