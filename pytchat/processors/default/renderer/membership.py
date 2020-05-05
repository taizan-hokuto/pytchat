from .base import BaseRenderer


class LiveChatMembershipItemRenderer(BaseRenderer):
    def __init__(self, item):
        super().__init__(item, "newSponsor")

    def get_authordetails(self):
        super().get_authordetails()
        self.author.isChatSponsor = True

    def get_message(self, renderer):
        message = ''.join([mes.get("text", "") for mes in renderer["headerSubtext"]["runs"]])
        return message, [message]

