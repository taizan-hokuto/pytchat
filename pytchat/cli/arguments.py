from typing import Optional, Dict, Union, List
from .singleton import Singleton

'''
This modules refer to
Petter Kraabøl's Twitch-Chat-Downloader
https://github.com/PetterKraabol/Twitch-Chat-Downloader
(MIT License)
'''


class Arguments(metaclass=Singleton):
    """
    Arguments singleton
    """

    class Name:
        VERSION: str = 'version'
        OUTPUT: str = 'output_dir'
        VIDEO_IDS: str = 'video_id'
        DEBUG: bool = 'debug'
        ECHO: bool = 'echo'

    def __init__(self,
                 arguments: Optional[Dict[str, Union[str, bool, int]]] = None):
        """
        Initialize arguments
        :param arguments: Arguments from cli
        (Optional to call singleton instance without parameters)
        """

        if arguments is None:
            print('Error: arguments were not provided')
            exit()

        self.print_version: bool = arguments[Arguments.Name.VERSION]
        self.output: str = arguments[Arguments.Name.OUTPUT]
        self.video_ids: List[int] = []
        self.debug: bool = arguments[Arguments.Name.DEBUG]
        self.echo: bool = arguments[Arguments.Name.ECHO]
        
        # Videos
        if arguments[Arguments.Name.VIDEO_IDS]:
            self.video_ids = [video_id
                              for video_id in arguments[Arguments.Name.VIDEO_IDS].split(',')]
