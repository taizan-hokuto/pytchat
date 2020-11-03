import re
from . import currency
from .base import BaseRenderer
superchat_regex = re.compile(r"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$")


class Colors2:
    pass


class LiveChatPaidStickerRenderer(BaseRenderer):
    def settype(self):
        self.chat.type = "superSticker"

    def get_snippet(self):
        super().get_snippet()
        amountDisplayString, symbol, amount = (
            self.get_amountdata(self.item)
        )
        self.chat.amountValue = amount
        self.chat.amountString = amountDisplayString
        self.chat.currency = currency.symbols[symbol]["fxtext"] if currency.symbols.get(
            symbol) else symbol
        self.chat.bgColor = self.item.get("backgroundColor", 0)
        self.chat.sticker = "".join(("https:",
            self.item["sticker"]["thumbnails"][0]["url"]))
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
        colors = Colors2()
        colors.moneyChipBackgroundColor = item.get("moneyChipBackgroundColor", 0)
        colors.moneyChipTextColor = item.get("moneyChipTextColor", 0)
        colors.backgroundColor = item.get("backgroundColor", 0)
        colors.authorNameTextColor = item.get("authorNameTextColor", 0)
        return colors
