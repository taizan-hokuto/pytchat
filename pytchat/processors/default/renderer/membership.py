from .base import BaseRenderer


class LiveChatMembershipItemRenderer(BaseRenderer):
    def settype(self):
        self.chat.type = "newSponsor"

    def get_authordetails(self):
        super().get_authordetails()
        self.chat.author.isChatSponsor = True

    def get_message(self, item):
        try:
            message = ''.join([mes.get("text", "")
                           for mes in item["headerSubtext"]["runs"]])
        except KeyError:
            return "Welcome New Member!", ["Welcome New Member!"]
        return message, [message]
