from datetime import datetime


class Author:
    pass


class BaseRenderer:
    def setitem(self, item, chat):
        self.item = item
        self.chat = chat
        self.chat.author = Author()

    def settype(self):
        pass

    def get_snippet(self):
        self.chat.id = self.item.get('id')
        timestampUsec = int(self.item.get("timestampUsec", 0))
        self.chat.timestamp = int(timestampUsec / 1000)
        tst = self.item.get("timestampText")
        if tst:
            self.chat.elapsedTime = tst.get("simpleText")
        else:
            self.chat.elapsedTime = ""
        self.chat.datetime = self.get_datetime(timestampUsec)
        self.chat.message, self.chat.messageEx = self.get_message(self.item)
        self.chat.id = self.item.get('id')
        self.chat.amountValue = 0.0
        self.chat.amountString = ""
        self.chat.currency = ""
        self.chat.bgColor = 0

    def get_authordetails(self):
        self.chat.author.badgeUrl = ""
        (self.chat.author.isVerified,
         self.chat.author.isChatOwner,
         self.chat.author.isChatSponsor,
         self.chat.author.isChatModerator) = (
            self.get_badges(self.item)
        )
        self.chat.author.channelId = self.item.get("authorExternalChannelId")
        self.chat.author.channelUrl = "http://www.youtube.com/channel/" + self.chat.author.channelId
        self.chat.author.name = self.item["authorName"]["simpleText"]
        self.chat.author.imageUrl = self.item["authorPhoto"]["thumbnails"][1]["url"]

    def get_message(self, item):
        message = ''
        message_ex = []
        runs = item.get("message", {}).get("runs", {})
        for r in runs:
            if not hasattr(r, "get"):
                continue
            if r.get('emoji'):
                message += r['emoji'].get('shortcuts', [''])[0]
                message_ex.append({
                    'id': r['emoji'].get('emojiId').split('/')[-1],
                    'txt': r['emoji'].get('shortcuts', [''])[0],
                    'url': r['emoji']['image']['thumbnails'][0].get('url')
                })
            else:
                message += r.get('text', '')
                message_ex.append(r.get('text', ''))
        return message, message_ex

    def get_badges(self, renderer):
        self.chat.author.type = ''
        isVerified = False
        isChatOwner = False
        isChatSponsor = False
        isChatModerator = False
        badges = renderer.get("authorBadges", {})
        for badge in badges:
            if badge["liveChatAuthorBadgeRenderer"].get("icon"):
                author_type = badge["liveChatAuthorBadgeRenderer"]["icon"]["iconType"]
                self.chat.author.type = author_type
                if author_type == 'VERIFIED':
                    isVerified = True
                if author_type == 'OWNER':
                    isChatOwner = True
                if author_type == 'MODERATOR':
                    isChatModerator = True
            if badge["liveChatAuthorBadgeRenderer"].get("customThumbnail"):
                isChatSponsor = True
                self.chat.author.type = 'MEMBER'
                self.get_badgeurl(badge)
        return isVerified, isChatOwner, isChatSponsor, isChatModerator

    def get_badgeurl(self, badge):
        self.chat.author.badgeUrl = badge["liveChatAuthorBadgeRenderer"]["customThumbnail"]["thumbnails"][0]["url"]

    def get_datetime(self, timestamp):
        dt = datetime.fromtimestamp(timestamp / 1000000)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def get_chatobj(self):
        return self.chat

    def clear(self):
        self.item = None
        self.chat = None
