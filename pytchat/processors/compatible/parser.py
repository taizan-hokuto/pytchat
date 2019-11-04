
from .renderer.textmessage import LiveChatTextMessageRenderer
from .renderer.paidmessage import LiveChatPaidMessageRenderer
from .renderer.paidsticker import LiveChatPaidStickerRenderer
from .renderer.legacypaid import LiveChatLegacyPaidMessageRenderer

class Parser:
    def parse(self, sitem):

        action = sitem.get("addChatItemAction")
        if action:
            item = action.get("item")
        if item is None: return None
        rd={}
        try:
            renderer = self.get_renderer(item)
            if renderer == None:
                return None

            rd["kind"] = "youtube#liveChatMessage"
            rd["etag"] = ""
            rd["id"] = 'LCC.' + renderer.get_id()
            rd["snippet"]       = renderer.get_snippet()
            rd["authorDetails"] = renderer.get_authordetails()
        except (KeyError,TypeError,AttributeError) as e:
            print(f"------{str(type(e))}-{str(e)}----------")
            print(sitem)
            return None
        
        return rd        

    def get_renderer(self, item):
        if item.get("liveChatTextMessageRenderer"):
            renderer = LiveChatTextMessageRenderer(item)
        elif item.get("liveChatPaidMessageRenderer"):
            renderer = LiveChatPaidMessageRenderer(item)
        elif item.get( "liveChatPaidStickerRenderer"):
            renderer = LiveChatPaidStickerRenderer(item)
        elif item.get("liveChatLegacyPaidMessageRenderer"):
            renderer = LiveChatLegacyPaidMessageRenderer(item)
        else:
            renderer = None
        return renderer

