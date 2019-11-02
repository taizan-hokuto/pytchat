from . import parser
import json
import os
import traceback
import datetime
import time
class CompatibleProcessor():
    
    def process(self, chat_components: list):

        chatlist = []
        timeout = 0
        ret={}
        ret["kind"] = "youtube#liveChatMessageListResponse"
        ret["etag"] = ""
        ret["nextPageToken"] = ""

        if chat_components:
            for chat_component in chat_components:
                timeout += chat_component.get('timeout', 0)
                chatdata = chat_component.get('chatdata')
             
                if chatdata is None: break
                for action in chatdata:
                    if action is None: continue
                    if action.get('addChatItemAction') is None: continue
                    if action['addChatItemAction'].get('item') is None: continue

                    chat = parser.parse(action)
                    if chat:
                        chatlist.append(chat)
        ret["pollingIntervalMillis"] = int(timeout*1000)
        ret["pageInfo"]={
            "totalResults":len(chatlist),
            "resultsPerPage":len(chatlist),
        }
        ret["items"] = chatlist

        return ret