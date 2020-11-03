import re
from . import currency
from .base import BaseRenderer
superchat_regex = re.compile(r"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$")


class Colors:
    pass


class LiveChatPaidMessageRenderer(BaseRenderer):
    def settype(self):
        self.chat.type = "superChat"

    def get_snippet(self):
        super().get_snippet()
        amountDisplayString, symbol, amount = (
            self.get_amountdata(self.item)
        )
        self.chat.amountValue = amount
        self.chat.amountString = amountDisplayString
        self.chat.currency = currency.symbols[symbol]["fxtext"] if currency.symbols.get(
            symbol) else symbol
        self.chat.bgColor = self.item.get("bodyBackgroundColor", 0)
        self.chat.colors = self.get_colors()

    def get_amountdata(self, item):
        amountDisplayString = item["purchaseAmountText"]["simpleText"]
        m = superchat_regex.search(amountDisplayString)
        if m:
            symbol = m.group(1)
            amount = float(m.group(2).replace(',', ''))
        else:
            symbol = ""
            amount = 0.0
        return amountDisplayString, symbol, amount

    def get_colors(self):
        item = self.item
        colors = Colors()
        colors.headerBackgroundColor = item.get("headerBackgroundColor", 0)
        colors.headerTextColor = item.get("headerTextColor", 0)
        colors.bodyBackgroundColor = item.get("bodyBackgroundColor", 0)
        colors.bodyTextColor = item.get("bodyTextColor", 0)
        colors.timestampColor = item.get("timestampColor", 0)
        colors.authorNameTextColor = item.get("authorNameTextColor", 0)
        return colors
