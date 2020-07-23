import re
from . import currency
from .base import BaseRenderer
superchat_regex = re.compile(r"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$")


class Colors:
    pass


class LiveChatPaidStickerRenderer(BaseRenderer):
    def __init__(self, item):
        super().__init__(item, "superSticker")

    def get_snippet(self):
        super().get_snippet()
        amountDisplayString, symbol, amount = (
            self.get_amountdata(self.renderer)
        )
        self.amountValue = amount
        self.amountString = amountDisplayString
        self.currency = currency.symbols[symbol]["fxtext"] if currency.symbols.get(
            symbol) else symbol
        self.bgColor = self.renderer.get("moneyChipBackgroundColor", 0)
        self.sticker = "".join(("https:",
            self.renderer["sticker"]["thumbnails"][0]["url"]))
        self.colors = self.get_colors()

    def get_amountdata(self, renderer):
        amountDisplayString = renderer["purchaseAmountText"]["simpleText"]
        m = superchat_regex.search(amountDisplayString)
        if m:
            symbol = m.group(1)
            amount = float(m.group(2).replace(',', ''))
        else:
            symbol = ""
            amount = 0.0
        return amountDisplayString, symbol, amount

    def get_colors(self):
        colors = Colors()
        colors.moneyChipBackgroundColor = self.renderer.get("moneyChipBackgroundColor", 0)
        colors.moneyChipTextColor = self.renderer.get("moneyChipTextColor", 0)
        colors.backgroundColor = self.renderer.get("backgroundColor", 0)
        colors.authorNameTextColor = self.renderer.get("authorNameTextColor", 0)
        return colors
