pytchat
=======

pytchat is a python library for fetching youtube live chat.

## Description
pytchat is a python library for fetching youtube live chat
without using youtube api, Selenium or BeautifulSoup.

Other features:
+ Customizable chat data processors including yt api compatible one.
+ Available on asyncio context. 
+ Quick fetching of initial chat data by generating continuation params
instead of web scraping.

より詳細な説明は [wiki](https://github.com/taizan-hokuto/pytchat/wiki) をご参照ください。

## Install
```python
pip install pytchat
```
## Demo
![demo](https://taizan-hokuto.github.io/statics/demo.gif "demo")

## Examples
### on-demand mode
```python
from pytchat import LiveChat

chat = LiveChat("G1w62uEMZ74")
while chat.is_alive():
    data = chat.get()
    for c in data.items:
        print(f"{c.datetime} [{c.author.name}]-{c.message} {c.amountString}")
        data.tick()
```

### callback mode
```python
from pytchat import LiveChat
import time

chat = LiveChat("G1w62uEMZ74", callback = func)
while chat.is_alive():
    #other background operation here.
    time.sleep(3)

def func(chatdata):
    for c in chatdata.items:
        print(f"{c.datetime} [{c.author.name}]-{c.message} {c.amountString}")
        chat.tick()
```

### asyncio context:
```python
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


### yt api compatible processor:
```python
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
<table>
  <tr>
    <th>name</th>
    <th>type</th>
    <th>remarks</th>
  </tr>
  <tr>
    <td>type</td>
    <td>str</td>
    <td>"superChat","textMessage","superSticker","newSponsor"</td>
  </tr>
  <tr>
    <td>id</td>
    <td>str</td>
    <td></td>
  </tr>
  <tr>
    <td>message</td>
    <td>str</td>
    <td>emojis are represented by ":(shortcut text):"</td>
  </tr>
  <tr>
    <td>timestamp</td>
    <td>int</td>
    <td>unixtime milliseconds</td>
  </tr>
  <tr>
    <td>datetime</td>
    <td>str</td>
    <td></td>
  </tr>
  <tr>
    <td>amountValue</td>
    <td>float</td>
    <td>ex. 1,234.0</td>
  </tr>
  <tr>
    <td>amountString</td>
    <td>str</td>
    <td>ex. "$ 1,234"</td>
  </tr>
  <tr>
    <td>currency</td>
    <td>str</td>
    <td>ISO 4217 currency codes (ex. "USD")</td>
  </tr>
  <tr>
    <td>bgColor</td>
    <td>int</td>
    <td>RGB Int</td>
  </tr>
  <tr>
    <td>author</td>
    <td>object</td>
    <td>see below</td>
  </tr>
</table>

Structure of author object.
<table>
  <tr>
    <th>name</th>
    <th>type</th>
    <th>remarks</th>
  </tr>
  <tr>
    <td>name</td>
    <td>str</td>
    <td></td>
  </tr>
  <tr>
    <td>channelId</td>
    <td>str</td>
    <td></td>
  </tr>
  <tr>
    <td>channelUrl</td>
    <td>str</td>
    <td></td>
  </tr>
  <tr>
    <td>imageUrl</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>badgeUrl</td>
    <td></td>
    <td></td>
  </tr>
  <tr>
    <td>isVerified</td>
    <td>bool</td>
    <td></td>
  </tr>
  <tr>
    <td>isChatOwner</td>
    <td>bool</td>
    <td></td>
  </tr>
  <tr>
    <td>isChatSponsor</td>
    <td>bool</td>
    <td></td>
  </tr>
  <tr>
    <td>isChatModerator</td>
    <td>bool</td>
    <td></td>
  </tr>
</table>

## Licence

[![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

## Author

[taizan-hokuto](https://github.com/taizan-hokuto)

[twitter:@taizan205](https://twitter.com/taizan205)