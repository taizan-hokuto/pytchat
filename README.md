## Install
```bash
pip install yvi
```


## Usage
```python
import yvi

info = yvi.get_info(video_id = "xxxxxxxx")
info.get_title()
info.get_channel_id()
```
## Function

### get_info(video_id, session)

Parameters
----------
- video_id : video id

- session : session object of requests.

Returns
-------
+ VideoInfo object.


## Attributes of VideoInfo object

### get_duration()
- 動画の長さ（秒。アーカイブのみ。ライブ動画または待機画面の場合、0が返ります。）

### get_title()
- 動画タイトル

### get_title_escaped()
- 動画タイトル(絵文字なし。GUIライブラリ等で絵文字が含まれていてエラーが出る場合はこちらを使用してください)

### get_channel_id()
- チャンネルID

### get_thumbnail()
- 動画サムネイルURL

### get_owner_name()
- 配信者名

### get_owner_name_escaped()
- 配信者名(絵文字なし)

### get_owner_image()
- 　　配信者プロフィール画像URL

### get_user_name()
- 視聴者名

### get_user_name_escaped()
- 視聴者名(絵文字なし)

### get_user_image()
- 視聴者プロフィール画像URL
