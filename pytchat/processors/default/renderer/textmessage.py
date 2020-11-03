from .base import BaseRenderer


class LiveChatTextMessageRenderer(BaseRenderer):
    def settype(self):
        self.chat.type = "textMessage"
