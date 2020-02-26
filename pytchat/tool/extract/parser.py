import json
from ... import config
from ... exceptions import ( 
    ResponseContextError, 
    NoContentsException, 
    NoContinuationsException )

logger = config.logger(__name__)

def parse(jsn):
    """
    Parse replay chat data.
    Parameter:
    ----------
    jsn : dict
        JSON of replay chat data.
    Returns:
    ------
        continuation : str
        actions : list

    """
    if jsn is None: 
        raise ValueError("parameter JSON is None")
    if jsn['response']['responseContext'].get('errors'):
        raise ResponseContextError(
    'video_id is invalid or private/deleted.')
    contents=jsn['response'].get('continuationContents')
    if contents is None:
        raise NoContentsException('No chat data.')

    cont = contents['liveChatContinuation']['continuations'][0]
    if cont is None:
        raise NoContinuationsException('No Continuation')
    metadata = cont.get('liveChatReplayContinuationData')
    if metadata:
        continuation = metadata.get("continuation")
        actions = contents['liveChatContinuation'].get('actions')
        return continuation, actions
    return None, []


def get_offset(item):
    return int(item['replayChatItemAction']["videoOffsetTimeMsec"])

def get_id(item):
    return list((list(item['replayChatItemAction']["actions"][0].values()
                )[0])['item'].values())[0].get('id')

def get_type(item):
    return list((list(item['replayChatItemAction']["actions"][0].values()
                )[0])['item'].keys())[0]


