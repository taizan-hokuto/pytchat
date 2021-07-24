from .base import BaseRenderer


class LiveChatDonationAnnouncementRenderer(BaseRenderer):
    def settype(self):
        self.chat.type = "donation"