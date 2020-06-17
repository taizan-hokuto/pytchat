from .chat_processor import ChatProcessor


class DummyProcessor(ChatProcessor):
    '''
    Dummy processor just returns received chat_components directly.
    '''

    def process(self, chat_components: list):
        return chat_components
