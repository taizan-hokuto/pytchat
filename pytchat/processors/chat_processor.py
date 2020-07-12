class ChatProcessor:
    '''
    Abstract class that processes chat data.
    Receive chat data (actions) from Listener.
    '''

    def process(self, chat_components: list):
        '''
        Interface that represents processing of chat data.
        Called from LiveChat object.

        Parameter
        ----------
        chat_components: List[component]
            component : dict {
                "video_id" : str
                "timeout"  : int
                    Time to fetch next chat (seconds)
                "chatdata" : List[dict]
                    List of chat data.
            }
        '''
        pass

    def finalize(self, *args, **kwargs):
        '''
        Interface for finalizing the process.
        Called when chat fetching finished.
        '''
        pass
