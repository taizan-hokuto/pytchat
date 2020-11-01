import httpx
import os
import re
import time
from base64 import standard_b64encode
from .chat_processor import ChatProcessor
from .default.processor import DefaultProcessor
from ..exceptions import UnknownConnectionError


PATTERN = re.compile(r"(.*)\(([0-9]+)\)$")

fmt_headers = ['datetime', 'elapsed', 'authorName',
               'message', 'superchat', 'type', 'authorChannel']

HEADER_HTML = '''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
'''

TABLE_CSS = '''
table.css {
 border-collapse: collapse;
}
 
table.css thead{
 border-collapse: collapse;
 border: 1px solid #000
}
 
table.css tr td{
 padding: 0.3em;
 border: 1px solid #000
}

table.css th{
 padding: 0.3em;
 border: 1px solid #000
}
'''


class HTMLArchiver(ChatProcessor):
    '''
    HTMLArchiver saves chat data as HTML table format.
    '''
    def __init__(self, save_path, callback=None):
        super().__init__()
        self.client = httpx.Client(http2=True)
        self.save_path = self._checkpath(save_path)
        self.processor = DefaultProcessor()
        self.emoji_table = {}  # tuble for custom emojis. key: emoji_id, value: base64 encoded image binary.
        self.header = [HEADER_HTML]
        self.body = ['<body>\n', '<table class="css">\n', self._parse_table_header(fmt_headers)]
        self.callback = callback

    def _checkpath(self, filepath):
        splitter = os.path.splitext(os.path.basename(filepath))
        body = splitter[0]
        extention = splitter[1]
        newpath = filepath
        counter = 1
        while os.path.exists(newpath):
            match = re.search(PATTERN, body)
            if match:
                counter = int(match[2]) + 1
                num_with_bracket = f'({str(counter)})'
                body = f'{match[1]}{num_with_bracket}'
            else:
                body = f'{body}({str(counter)})'
            newpath = os.path.join(os.path.dirname(filepath), body + extention)
        return newpath

    def process(self, chat_components: list):
        """
        Returns
        ----------
        dict :
            save_path : str :
                Actual save path of file.
            total_lines : int :
                count of total lines written to the file.
        """
        if chat_components is None or len(chat_components) == 0:
            return
        for c in self.processor.process(chat_components).items:
            self.body.extend(
                self._parse_html_line((
                    c.datetime,
                    c.elapsedTime,
                    c.author.name,
                    self._parse_message(c.messageEx),
                    c.amountString,
                    c.author.type,
                    c.author.channelId)
                )
            )
            if self.callback:
                self.callback(None, 1)

    def _parse_html_line(self, raw_line):
        return ''.join(('<tr>',
                        ''.join(''.join(('<td>', cell, '</td>')) for cell in raw_line),
                        '</tr>\n'))

    def _parse_table_header(self, raw_line):
        return ''.join(('<thead><tr>',
                        ''.join(''.join(('<th>', cell, '</th>')) for cell in raw_line),
                        '</tr></thead>\n'))
        
    def _parse_message(self, message_items: list) -> str:
        return ''.join(''.join(('<span class="', self._set_emoji_table(item), '" title="', item['txt'], '"></span>'))
                       if type(item) is dict else item
                       for item in message_items)

    def _encode_img(self, url):
        err = None
        for _ in range(5):
            try:
                resp = self.client.get(url, timeout=30)
                break
            except httpx.HTTPError as e:
                print("Network Error. retrying...")
                err = e
                time.sleep(3)
        else:
            raise UnknownConnectionError(str(err))

        return standard_b64encode(resp.content).decode()

    def _set_emoji_table(self, item: dict):
        emoji_id = item['id']
        if emoji_id not in self.emoji_table:
            self.emoji_table.setdefault(emoji_id, self._encode_img(item['url']))
        return emoji_id

    def _stylecode(self, name, code, width, height):
        return ''.join((".", name, " { display: inline-block; background-image: url(data:image/png;base64,",
                        code, "); background-repeat: no-repeat; width: ",
                        str(width), "; height: ", str(height), ";}"))
    
    def _create_styles(self):
        return '\n'.join(('<style type="text/css">',
                          TABLE_CSS,
                          '\n'.join(self._stylecode(key, self.emoji_table[key], 24, 24)
                                for key in self.emoji_table.keys()),
                          '</style>\n'))
    
    def finalize(self):
        self.header.extend([self._create_styles(), '</head>\n'])
        self.body.extend(['</table>\n</body>\n</html>'])
        with open(self.save_path, mode='a', encoding='utf-8') as f:
            f.writelines(self.header)
            f.writelines(self.body)
