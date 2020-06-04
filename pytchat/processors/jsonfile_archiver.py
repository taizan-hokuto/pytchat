import json
import os
import re
from .chat_processor import ChatProcessor

PATTERN = re.compile(r"(.*)\(([0-9]+)\)$")


class JsonfileArchiver(ChatProcessor):
    """
    JsonfileArchiver saves chat data as text of JSON lines.

    Parameter:
    ----------
    save_path : str :
        save path of file.If a file with the same name exists,
        it is automatically saved under a different name
        with suffix '(number)'
    """

    def __init__(self, save_path):
        super().__init__()
        self.save_path = self._checkpath(save_path)
        self.line_counter = 0

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
        if chat_components is None:
            return
        with open(self.save_path, mode='a', encoding='utf-8') as f:
            for component in chat_components:
                if component is None:
                    continue
                chatdata = component.get('chatdata')
                if chatdata is None:
                    continue
                for action in chatdata:
                    if action is None:
                        continue
                    json_line = json.dumps(action, ensure_ascii=False)
                    f.writelines(json_line + '\n')
                    self.line_counter += 1
            return {"save_path": self.save_path,
                    "total_lines": self.line_counter}

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
