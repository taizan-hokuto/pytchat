import re
from . import currency
from .base import BaseRenderer
superchat_regex = re.compile(r"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$")


class LiveChatPaidMessageRenderer(BaseRenderer):
    def __init__(self, item):
        super().__init__(item, "superChatEvent")

    def get_snippet(self):
        authorName = self.renderer["authorName"]["simpleText"]
        message = self.get_message(self.renderer)
        amountDisplayString, symbol, amountMicros = (
            self.get_amountdata(self.renderer)
        )
        return {
            "type": self.chattype,
            "liveChatId": "",
            "authorChannelId": self.renderer.get("authorExternalChannelId"),
            "publishedAt": self.get_publishedat(self.renderer.get("timestampUsec", 0)),
            "hasDisplayContent": True,
            "displayMessage": amountDisplayString + " from " + authorName + ': \"' + message + '\"',
            "superChatDetails": {
                "amountMicros": amountMicros,
                "currency": currency.symbols[symbol]["fxtext"] if currency.symbols.get(symbol) else symbol,
                "amountDisplayString": amountDisplayString,
                "tier": 0,
                "backgroundColor": self.renderer.get("bodyBackgroundColor", 0)
            }
        }

    def get_amountdata(self, renderer):
        amountDisplayString = renderer["purchaseAmountText"]["simpleText"]
        m = superchat_regex.search(amountDisplayString)
        if m:
            symbol = m.group(1)
            amountMicros = int(float(m.group(2).replace(',', '')) * 1000000)
        else:
            symbol = ""
            amountMicros = 0
        return amountDisplayString, symbol, amountMicros
