import csv
import os
import re
from .chat_processor import ChatProcessor
from .default.processor import DefaultProcessor

PATTERN = re.compile(r"(.*)\(([0-9]+)\)$")
fmt_headers = ['datetime', 'elapsed', 'authorName', 'message',
               'superchatAmount', 'authorType', 'authorChannel']


class TSVArchiver(ChatProcessor):
    '''
    TsvArchiver saves chat data as Tab Separated Values format text.
    '''

    def __init__(self, save_path):
        super().__init__()
        self.save_path = self._checkpath(save_path)
        with open(self.save_path, mode='a', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(fmt_headers)
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
            writer = csv.writer(f, delimiter='\t')
            chats = self.processor.process(chat_components).items
            for c in chats:
                writer.writerow([
                    c.datetime,
                    c.elapsedTime,
                    c.author.name,
                    c.message,
                    c.amountString,
                    c.author.type,
                    c.author.channelId
                ])
