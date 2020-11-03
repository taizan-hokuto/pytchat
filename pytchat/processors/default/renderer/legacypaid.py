from .base import BaseRenderer


class LiveChatLegacyPaidMessageRenderer(BaseRenderer):
    def settype(self):
        self.chat.type = "newSponsor"

    def get_authordetails(self):
        super().get_authordetails()
        self.chat.author.isChatSponsor = True

    def get_message(self, item):
        message = (item["eventText"]["runs"][0]["text"]
                   ) + ' / ' + (item["detailText"]["simpleText"])
        return message, [message]
