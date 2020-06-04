from .base import BaseRenderer


class LiveChatTextMessageRenderer(BaseRenderer):
    def __init__(self, item):
        super().__init__(item, "textMessageEvent")
