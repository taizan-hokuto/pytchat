import pytchat
from pytchat.processors.compatible.processor import CompatibleProcessor


root_keys = ('kind', 'etag', 'nextPageToken', 'pollingIntervalMillis', 'pageInfo', 'items')
item_keys = ('kind', 'etag', 'id', 'snippet', 'authorDetails')
snippet_keys = ('type', 'liveChatId', 'authorChannelId', 'publishedAt', 'hasDisplayContent', 'displayMessage', 'textMessageDetails')
author_details_keys = ('channelId', 'channelUrl', 'displayName', 'profileImageUrl', 'isVerified', 'isChatOwner', 'isChatSponsor', 'isChatModerator')

def test_compatible_processor():
    stream = pytchat.create("Hj-wnLIYKjw", seektime = 6000, processor=CompatibleProcessor())
    while stream.is_alive():
        chat = stream.get()
        for key in chat.keys():
            assert key in root_keys
        for key in chat["items"][0].keys():
            assert key in item_keys
        for key in chat["items"][0]["snippet"].keys():
            assert key in snippet_keys
        for key in chat["items"][0]["authorDetails"].keys():
            assert key in author_details_keys
        break

    