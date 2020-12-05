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
    if jsn.get("error") or jsn.get("responseContext", {}).get("errors"):
        raise exceptions.ResponseContextError(
            'video_id is invalid or private/deleted.')
    contents = jsn.get('continuationContents')
    if contents is None:
        raise exceptions.NoContents('No chat data.')

    cont = contents['liveChatContinuation']['continuations'][0]
    if cont is None:
        raise exceptions.NoContinuation('No Continuation')
    metadata = cont.get('liveChatReplayContinuationData')
    if metadata:
        visitor_data = jsn.get("responseContext", {}).get("visitorData", '')
        continuation = metadata.get("continuation")
        actions: list = contents['liveChatContinuation'].get('actions')
        last_offset: int = get_offset(actions[-1]) if actions else 0
        return continuation, actions, last_offset, visitor_data
    return None, [], 0, ''


def get_offset(item) -> int:
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
