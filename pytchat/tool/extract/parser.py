from ... import config
from ... import exceptions

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
        raise exceptions.ResponseContextError(
            'video_id is invalid or private/deleted.')
    contents = jsn['response'].get('continuationContents')
    if contents is None:
        raise exceptions.NoContents('No chat data.')

    cont = contents['liveChatContinuation']['continuations'][0]
    if cont is None:
        raise exceptions.NoContinuation('No Continuation')
    metadata = cont.get('liveChatReplayContinuationData')
    if metadata:
        continuation = metadata.get("continuation")
        actions = contents['liveChatContinuation'].get('actions')
        return continuation, actions
    return None, []


def get_offset(item):
    return int(item['replayChatItemAction']["videoOffsetTimeMsec"])


def get_id(item):
    a = list(item['replayChatItemAction']["actions"][0].values())[0].get('item')
    if a:
        return list(a.values())[0].get('id')
    return None


def get_type(item):
    a = list(item['replayChatItemAction']["actions"][0].values())[0].get('item')
    if a:
        return list(a.keys())[0]
    return None
