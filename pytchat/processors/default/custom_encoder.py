import json
from .renderer.base import Author
from .renderer.paidmessage import Colors
from .renderer.paidsticker import Colors2


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Author) or isinstance(obj, Colors) or isinstance(obj, Colors2):
            return vars(obj)
        return json.JSONEncoder.default(self, obj)
