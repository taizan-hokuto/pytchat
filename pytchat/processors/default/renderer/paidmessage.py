import re
from . import currency
from .base import BaseRenderer
superchat_regex = re.compile(r"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$")


class LiveChatPaidMessageRenderer(BaseRenderer):
    def __init__(self, item):
        super().__init__(item, "superChat")

    def get_snippet(self):
        super().get_snippet()
        amountDisplayString, symbol, amount = (
            self.get_amountdata(self.renderer)
        )
        self.amountValue = amount
        self.amountString = amountDisplayString
        self.currency = currency.symbols[symbol]["fxtext"] if currency.symbols.get(
            symbol) else symbol
        self.bgColor = self.renderer.get("bodyBackgroundColor", 0)

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
