"""
pytchat.parser.live
~~~~~~~~~~~~~~~~~~~
Parser of live chat JSON.
"""

import json
from .. exceptions import ( 
    ResponseContextError, 
    NoContentsException, 
    NoContinuationsException,
    ChatParseException )

class Parser:

    __slots__ = ['is_replay']
    
    def __init__(self, is_replay): 
        self.is_replay = is_replay

    def get_contents(self, jsn):
        if jsn is None: 
            raise ChatParseException('Called with none JSON object.')
        if jsn['response']['responseContext'].get('errors'):
            raise ResponseContextError('The video_id would be wrong,'
                'or video is deleted or private.')
        contents=jsn['response'].get('continuationContents')
        return contents

    def parse(self, contents):
        """
        Parameter
        ----------
        + contents : dict
            + JSON of chat data from YouTube.

        Returns
        -------
        tuple:
        + metadata : dict
         + timeout
         + video_id
         + continuation           
        + chatdata : List[dict]
        """

        if contents is None:
            '''Broadcasting end or cannot fetch chat stream'''
            raise NoContentsException('Chat data stream is empty.')

        cont = contents['liveChatContinuation']['continuations'][0]
        if cont is None:
            raise NoContinuationsException('No Continuation')
        metadata = (cont.get('invalidationContinuationData')  or
                    cont.get('timedContinuationData')         or
                    cont.get('reloadContinuationData')        or
                    cont.get('liveChatReplayContinuationData')
                    )
        if metadata is None:
            if cont.get("playerSeekContinuationData"):
                raise ChatParseException('Finished chat data')
            unknown = list(cont.keys())[0]
            if unknown:
                raise ChatParseException(f"Received unknown continuation type:{unknown}")
            else:
                raise ChatParseException('Cannot extract continuation data')
        return self._create_data(metadata, contents)

    def _create_data(self, metadata, contents):    
        actions = contents['liveChatContinuation'].get('actions')
        if self.is_replay:    
            interval = self._get_interval(actions)
            metadata.setdefault("timeoutMs",interval)
            """Archived chat has different structures than live chat, 
            so make it the same format."""
            chatdata = [action["replayChatItemAction"]["actions"][0]
                for action in actions]
        else:
            metadata.setdefault('timeoutMs', 10000)
            chatdata = actions
        return metadata, chatdata

    def _get_interval(self, actions: list):
        if actions is None:
            return 0
        start = int(actions[0]["replayChatItemAction"]["videoOffsetTimeMsec"])
        last = int(actions[-1]["replayChatItemAction"]["videoOffsetTimeMsec"])
        return (last - start)