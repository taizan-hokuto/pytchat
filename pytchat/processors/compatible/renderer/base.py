from datetime import datetime, timedelta, timezone

TZ_UTC = timezone(timedelta(0), 'UTC')


class BaseRenderer:
    def __init__(self, item, chattype):
        self.renderer = list(item.values())[0]
        self.chattype = chattype

    def get_snippet(self):

        message = self.get_message(self.renderer)

        return {
            "type": self.chattype,
            "liveChatId": "",
            "authorChannelId": self.renderer.get("authorExternalChannelId"),
            "publishedAt": self.get_publishedat(self.renderer.get("timestampUsec", 0)),
            "hasDisplayContent": True,
            "displayMessage": message,
            "textMessageDetails": {
                "messageText": message
            }
        }

    def get_authordetails(self):
        authorExternalChannelId = self.renderer.get("authorExternalChannelId")
        # parse subscriber type
        isVerified, isChatOwner, isChatSponsor, isChatModerator = (
            self.get_badges(self.renderer)
        )
        return {
            "channelId": authorExternalChannelId,
            "channelUrl": "http://www.youtube.com/channel/" + authorExternalChannelId,
            "displayName": self.renderer["authorName"]["simpleText"],
            "profileImageUrl": self.renderer["authorPhoto"]["thumbnails"][1]["url"],
            "isVerified": isVerified,
            "isChatOwner": isChatOwner,
            "isChatSponsor": isChatSponsor,
            "isChatModerator": isChatModerator
        }

    def get_message(self, renderer):
        message = ''
        if renderer.get("message"):
            runs = renderer["message"].get("runs")
            if runs:
                for r in runs:
                    if r:
                        if r.get('emoji'):
                            message += r['emoji'].get('shortcuts', [''])[0]
                        else:
                            message += r.get('text', '')
        return message

    def get_badges(self, renderer):
        isVerified = False
        isChatOwner = False
        isChatSponsor = False
        isChatModerator = False
        badges = renderer.get("authorBadges")
        if badges:
            for badge in badges:
                author_type = badge["liveChatAuthorBadgeRenderer"]["accessibility"]["accessibilityData"]["label"]
                if author_type == 'VERIFIED' or author_type == '確認済み':
                    isVerified = True
                if author_type == 'OWNER' or author_type == '所有者':
                    isChatOwner = True
                if 'メンバー' in author_type or 'MEMBER' in author_type:
                    isChatSponsor = True
                if author_type == 'MODERATOR' or author_type == 'モデレーター':
                    isChatModerator = True
        return isVerified, isChatOwner, isChatSponsor, isChatModerator

    def get_id(self):
        return self.renderer.get('id')

    def get_publishedat(self, timestamp):
        dt = datetime.fromtimestamp(int(timestamp) / 1000000)
        return dt.astimezone(TZ_UTC).isoformat(
            timespec='milliseconds').replace('+00:00', 'Z')
