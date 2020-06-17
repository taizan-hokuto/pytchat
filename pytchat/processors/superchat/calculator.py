import re
from pytchat.processors.chat_processor import ChatProcessor

superchat_regex = re.compile(r"^(\D*)(\d{1,3}(,\d{3})*(\.\d*)*\b)$")

items_paid = [
    'addChatItemAction',
    'item',
    'liveChatPaidMessageRenderer'
]

items_sticker = [
    'addChatItemAction',
    'item',
    'liveChatPaidStickerRenderer'
]


class SuperchatCalculator(ChatProcessor):
    """
    Calculate the amount of SuperChat by currency.
    """

    def __init__(self):
        self.results = {}

    def process(self, chat_components: list):
        """
        Return
        ------------
        results : dict :
            List of amount by currency.
            key: currency symbol, value: total amount.
        """
        if chat_components is None:
            return self.results
        for component in chat_components:
            chatdata = component.get('chatdata')
            if chatdata is None:
                continue
            for action in chatdata:
                renderer = self._get_item(action, items_paid) or \
                    self._get_item(action, items_sticker)
                if renderer is None:
                    continue
                symbol, amount = self._parse(renderer)
                self.results.setdefault(symbol, 0)
                self.results[symbol] += amount
        return self.results

    def _parse(self, renderer):
        purchase_amount_text = renderer["purchaseAmountText"]["simpleText"]
        m = superchat_regex.search(purchase_amount_text)
        if m:
            symbol = m.group(1)
            amount = float(m.group(2).replace(',', ''))
        else:
            symbol = ""
            amount = 0.0
        return symbol, amount

    def _get_item(self, dict_body, items: list):
        for item in items:
            if dict_body is None:
                break
            if isinstance(dict_body, dict):
                dict_body = dict_body.get(item)
                continue
            if isinstance(item, int) and \
               isinstance(dict_body, list) and \
               len(dict_body) > item:
                dict_body = dict_body[item]
                continue
            return None
        return dict_body
