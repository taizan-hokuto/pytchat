import json
import os
import datetime
from .chat_processor import ChatProcessor

class JsonfileArchiveProcessor(ChatProcessor):
    def __init__(self,filepath):
        super().__init__()
        if os.path.exists(filepath):
            print('filepath is already exists!: ')
            print('  '+filepath)
            newpath=os.path.dirname(filepath) + \
                '/'+datetime.datetime.now() \
                .strftime('%Y-%m-%d %H-%M-%S')+'.data'

            print('created alternate filename:')
            print('   '+newpath)
            self.filepath = newpath
        else:
            print('filepath: '+filepath)
            self.filepath = filepath

    def process(self,chat_components: list):
        if chat_components:
            with open(self.filepath, mode='a', encoding = 'utf-8') as f:
                for component in chat_components:
                    if component:
                        chatdata = component.get('chatdata')
                        for action in chatdata:
                            if action:
                                if action.get("addChatItemAction"):
                                    if action["addChatItemAction"]["item"].get(
                                    "liveChatViewerEngagementMessageRenderer"):
                                        continue
                                s = json.dumps(action,ensure_ascii = False)
                                #print(s[:200])
                                f.writelines(s+'\n')

    def _parsedir(self,_dir):
        if _dir[-1]=='\\' or _dir[-1]=='/':
            separator =''
        else:
            separator ='/'
        os.makedirs(_dir + separator, exist_ok=True)
        return _dir  + separator

