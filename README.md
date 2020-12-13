pytchat
=======

pytchat is a python library for fetching youtube live chat.
 

<br><br><br>
## Description
pytchat is a python library for fetching youtube live chat
without using Selenium or BeautifulSoup.

Other features:
+ Customizable [chat data processors](https://github.com/taizan-hokuto/pytchat/wiki/ChatProcessor) including youtube api compatible one.
+ Available on asyncio context. 
+ Quick fetching of initial chat data by generating continuation params
instead of web scraping.

For more detailed information, see [wiki](https://github.com/taizan-hokuto/pytchat/wiki). <br>
[wiki (Japanese)](https://github.com/taizan-hokuto/pytchat/wiki/Home_jp)

## Install
```python
pip install pytchat
```
## Examples


### Fetch chat data (see [wiki](https://github.com/taizan-hokuto/pytchat/wiki/PytchatCore))
```python
import pytchat
chat = pytchat.create(video_id="uIx8l2xlYVY")
while chat.is_alive():
    for c in chat.get().sync_items():
        print(f"{c.datetime} [{c.author.name}]- {c.message}")
```


### Output JSON format string (feature of [DefaultProcessor](https://github.com/taizan-hokuto/pytchat/wiki/DefaultProcessor))
```python
import pytchat
import time

chat = pytchat.create(video_id="uIx8l2xlYVY")
while chat.is_alive():
    print(chat.get().json())
    time.sleep(5)
    '''
    # Each chat item can also be output in JSON format.
    for c in chat.get().items:
        print(c.json())
    '''     
```


### other
+ Fetch chat with a buffer ([LiveChat](https://github.com/taizan-hokuto/pytchat/wiki/LiveChat))

+ Use with asyncio ([LiveChatAsync](https://github.com/taizan-hokuto/pytchat/wiki/LiveChatAsync))

+ YT API compatible chat processor ([CompatibleProcessor](https://github.com/taizan-hokuto/pytchat/wiki/CompatibleProcessor))


## Structure of Default Processor
Each item can be got with `sync_items()` function.
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
    <td>messageEx</td>
    <td>str</td>
    <td>list of message texts and emoji dicts(id, txt, url).</td>
  </tr>
  <tr>
    <td>timestamp</td>
    <td>int</td>
    <td>unixtime milliseconds</td>
  </tr>
  <tr>
    <td>datetime</td>
    <td>str</td>
    <td>e.g. "2019-10-10 12:34:56"</td>
  </tr>
    <td>elapsedTime</td>
    <td>str</td>
    <td>elapsed time. (e.g. "1:02:27") *Replay Only.</td>
  </tr>
  <tr>
    <td>amountValue</td>
    <td>float</td>
    <td>e.g. 1,234.0</td>
  </tr>
  <tr>
    <td>amountString</td>
    <td>str</td>
    <td>e.g. "$ 1,234"</td>
  </tr>
  <tr>
    <td>currency</td>
    <td>str</td>
    <td><a href="https://en.wikipedia.org/wiki/ISO_4217">ISO 4217 currency codes</a> (e.g. "USD")</td>
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
    <td>*chatter's channel ID.</td>
  </tr>
  <tr>
    <td>channelUrl</td>
    <td>str</td>
    <td></td>
  </tr>
  <tr>
    <td>imageUrl</td>
    <td>str</td>
    <td></td>
  </tr>
  <tr>
    <td>badgeUrl</td>
    <td>str</td>
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


