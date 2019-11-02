
from .renderer.textmessage import LiveChatTextMessageRenderer
from .renderer.paidmessage import LiveChatPaidMessageRenderer
from .renderer.paidsticker import LiveChatPaidStickerRenderer
from .renderer.legacypaid import LiveChatLegacyPaidMessageRenderer

def parse(sitem):

    action = sitem.get("addChatItemAction")
    if action:
        item = action.get("item")
    if item is None: return None
    try:
        renderer = get_renderer(item)
        if renderer == None:
            return None

        renderer.get_snippet()
        renderer.get_authordetails()
    except (KeyError,TypeError,AttributeError) as e:
        print(f"------{str(type(e))}-{str(e)}----------")
        print(sitem)
        return None
    
    return renderer        

def get_renderer(item):
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

