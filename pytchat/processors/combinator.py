from .chat_processor import ChatProcessor


class Combinator(ChatProcessor):
    '''
    Combinator combines multiple chat processors.
    Specify processors as tuple at `processor` params of LiveChat object.

    For example:
        [constructor]
        chat = LiveChat("video_id", processor = ( Processor1(), Processor2(), Processor3() ) )

        [receive return values]
        ret1, ret2, ret3 = chat.get()

    The return values are tuple of processed chat data,
    the order of return depends on parameter order.

    Parameter
    ---------
    processors : Tuple[ChatProcessor]
        multiple processors for processing chat data
    '''

    def __init__(self, processors: tuple):
        self.processors = processors

    def process(self, chat_components: list):
        '''
        Called from LiveChat.get() function by user,
        or LiveChat._listen() automatically.

        Returns
        -------
            Tuple of chat data processed by each chat processor.
        '''
        return tuple(processor.process(chat_components)
                     for processor in self.processors)

    def finalize(self, *args, **kwargs):
        [processor.finalize(*args, **kwargs)
                     for processor in self.processors]
