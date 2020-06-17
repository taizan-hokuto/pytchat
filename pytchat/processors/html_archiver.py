import os
import re
from .chat_processor import ChatProcessor
from .default.processor import DefaultProcessor

PATTERN = re.compile(r"(.*)\(([0-9]+)\)$")
fmt_headers = ['datetime', 'elapsed', 'authorName',
               'message', 'superchat', 'type', 'authorChannel']

HEADER_HTML = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8">
'''


class HTMLArchiver(ChatProcessor):
    '''
    HtmlArchiver saves chat data as HTML table format.
    '''

    def __init__(self, save_path):
        super().__init__()
        self.save_path = self._checkpath(save_path)
        with open(self.save_path, mode='a', encoding='utf-8') as f:
            f.write(HEADER_HTML)
            f.write('<table border="1" style="border-collapse: collapse">')
            f.writelines(self._parse_html_header(fmt_headers))
        self.processor = DefaultProcessor()

    def _checkpath(self, filepath):
        splitter = os.path.splitext(os.path.basename(filepath))
        body = splitter[0]
        extention = splitter[1]
        newpath = filepath
        counter = 0
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

        with open(self.save_path, mode='a', encoding='utf-8') as f:
            chats = self.processor.process(chat_components).items
            for c in chats:
                f.writelines(
                    self._parse_html_line([
                        c.datetime,
                        c.elapsedTime,
                        c.author.name,
                        c.message,
                        c.amountString,
                        c.author.type,
                        c.author.channelId]
                    )
                )
            '''
            #Palliative treatment#
            Comment out below line to prevent the table
            display from collapsing.
            '''
            # f.write('</table>')

    def _parse_html_line(self, raw_line):
        html = ''
        html += ' <tr>'
        for cell in raw_line:
            html += '<td>' + cell + '</td>'
        html += '</tr>\n'
        return html

    def _parse_html_header(self, raw_line):
        html = ''
        html += '<thead>\n'
        html += ' <tr>'
        for cell in raw_line:
            html += '<th>' + cell + '</th>'
        html += '</tr>\n'
        html += '</thead>\n'
        return html
