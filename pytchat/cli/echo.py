import pytchat
from ..exceptions import ChatDataFinished, NoContents
from ..util.extract_video_id import extract_video_id


class Echo:
    def __init__(self, video_id):
        self.video_id = extract_video_id(video_id)
    
    def run(self):
        livechat = pytchat.create(self.video_id)
        while livechat.is_alive():
            chatdata = livechat.get()
            for c in chatdata.sync_items():
                print(f"{c.datetime} [{c.author.name}] {c.message} {c.amountString}")
        
        try:
            livechat.raise_for_status()
        except (ChatDataFinished, NoContents):
            print("Chat finished.")
        except Exception as e:
            print(type(e), str(e))
