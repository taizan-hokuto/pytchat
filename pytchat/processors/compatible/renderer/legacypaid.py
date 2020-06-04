from .base import BaseRenderer


class LiveChatLegacyPaidMessageRenderer(BaseRenderer):
    def __init__(self, item):
        super().__init__(item, "newSponsorEvent")

    def get_snippet(self):

        message = self.get_message(self.renderer)

        return {
            "type": self.chattype,
            "liveChatId": "",
            "authorChannelId": self.renderer.get("authorExternalChannelId"),
            "publishedAt": self.get_publishedat(self.renderer.get("timestampUsec", 0)),
            "hasDisplayContent": True,
            "displayMessage": message,

        }

    def get_authordetails(self):
        authorExternalChannelId = self.renderer.get("authorExternalChannelId")
        # parse subscriber type
        isVerified, isChatOwner, _, isChatModerator = (
            self.get_badges(self.renderer)
        )
        return {
            "channelId": authorExternalChannelId,
            "channelUrl": "http://www.youtube.com/channel/" + authorExternalChannelId,
            "displayName": self.renderer["authorName"]["simpleText"],
            "profileImageUrl": self.renderer["authorPhoto"]["thumbnails"][1]["url"],
            "isVerified": isVerified,
            "isChatOwner": isChatOwner,
            "isChatSponsor": True,
            "isChatModerator": isChatModerator
        }

    def get_message(self, renderer):
        message = (renderer["eventText"]["runs"][0]["text"]
                   ) + ' / ' + (renderer["detailText"]["simpleText"])
        return message
