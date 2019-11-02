import re
from . import currency
from .paidmessage import LiveChatPaidMessageRenderer

class LiveChatPaidStickerRenderer(LiveChatPaidMessageRenderer):
    def __init__(self, item):
        super().__init__(item, "superSticker")


 

 

