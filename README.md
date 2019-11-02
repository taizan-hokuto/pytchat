
pytchat
=======

pytchat is a python library for fetching youtube live chat.

## Description
pytchat is a python library for fetching youtube live chat.
without using youtube api, Selenium or BeautifulSoup.

Other features:
+ Customizable chat data processors including yt api compatible one.
+ Available on asyncio context. 
+ Quick fetching of initial chat data by generating continuation params
instead of web scraping.

## Install
```
pip install pytchat
```

## Examples
```
from pytchat import LiveChat

chat = LiveChat("G1w62uEMZ74")
while chat.is_alive():
    data = chat.get()
    for c in data.items:
        print(f"{c.datetime} [{c.author.name}]-{c.message} {c.amountString}")
        data.tick()
```

callback mode
```
from pytchat import LiveChat

chat = LiveChat("G1w62uEMZ74", callback = func)
while chat.is_alive():
    time.sleep(3)

def func(chatdata):
    for c in chatdata.items:
        print(f"{c.datetime} [{c.author.name}]-{c.message} {c.amountString}")
        chat.tick()
```

asyncio context:
```
from pytchat import LiveChatAsync
import asyncio

async def main():
    chat = LiveChatAsync("G1w62uEMZ74", callback = func)
    while chat.is_alive():
        #other background operation here.
        await asyncio.sleep(3)

async def func(chat)
    for c in chat.items:
        print(f"{c.datetime} [{c.author.name}]-{c.message} {c.amountString}")
        await chat.tick_async()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```


yt api compatible processor:
```
from pytchat import LiveChat, CompatibleProcessor

chat = LiveChat("G1w62uEMZ74", 
     processor = CompatibleProcessor() )

while chat.is_alive():
    data = chat.get()
    polling = data["pollingIntervalMillis"]/1000
    for c in data["items"]:
        if c.get("snippet"):
            print(f"[{c['authorDetails']['displayName']}]"
                    f"-{c['snippet']['displayMessage']}")
            time.sleep(polling/len(data["items"]))

```


## Chatdata Structure of Default Processor
Structure of each item which got from items() function.
|name|type|remarks|
|:----|:----|:----|
|type|str|"superChat","textMessage","superSticker","newSponsor"|
|id|str||
|message|str|emojis are represented by ":(shortcut text):"|
|datetime|str|YYYY-mm-dd HH:MM:SS format|
|timestamp|int|unixtime milliseconds|
|amountValue|float|ex. 1,234.0|
|amountString|str|ex. "$ 1,234"|
|currency|str|ex. "USD"|
|author|object|see below|

Structure of author object.
|name|type|remarks|
|:----|:----|:----|
|name|str||
|channelId|str|authorExternalChannelId|
|channelUrl|str||
|imageUrl|str||
|badgeUrl|str||
|isVerified|bool||
|isChatOwner|bool||
|isChatSponsor|bool||
|isChatModerator|bool||
## Licence

[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

## Author

[taizan-hokuto](https://github.com/taizan-hokuto)