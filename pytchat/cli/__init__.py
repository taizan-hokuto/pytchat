import argparse
try:
    from asyncio import CancelledError
except ImportError:
    from asyncio.futures import CancelledError
import os
from .arguments import Arguments
from .echo import Echo
from .. exceptions import InvalidVideoIdException
from .. import __version__
from .cli_extractor import CLIExtractor


'''
Most of CLI modules refer to
Petter Kraabøl's Twitch-Chat-Downloader
https://github.com/PetterKraabol/Twitch-Chat-Downloader
(MIT License)
'''


def main():
    # Arguments
    parser = argparse.ArgumentParser(description=f'pytchat v{__version__}')
    parser.add_argument('-v', f'--{Arguments.Name.VIDEO_IDS}', type=str,
                        help='Video ID (or URL that includes Video ID). You can specify multiple video IDs by '
                        'separating them with commas without spaces.\n'
                        'If ID starts with a hyphen (-), enclose the ID in square brackets.')
    parser.add_argument('-o', f'--{Arguments.Name.OUTPUT}', type=str,
                        help='Output directory (end with "/"). default="./"', default='./')
    parser.add_argument(f'--{Arguments.Name.DEBUG}', action='store_true',
                        help='Debug mode. Stop when exceptions have occurred and save error data (".dat" file).')
    parser.add_argument(f'--{Arguments.Name.VERSION}', action='store_true',
                        help='Show version.')
    parser.add_argument(f'--{Arguments.Name.ECHO}', action='store_true',
        help='Display chats of specified video.')

    Arguments(parser.parse_args().__dict__)

    if Arguments().print_version:
        print(f'pytchat v{__version__}     © 2019, 2020 taizan-hokuto')
        return

    if not Arguments().video_ids:
        parser.print_help()
        return

    # Echo
    if Arguments().echo:
        if len(Arguments().video_ids) > 1:
            print("When using --echo option, only one video ID can be specified.")
            return
        try:
            Echo(Arguments().video_ids[0]).run()
        except InvalidVideoIdException as e:
            print("Invalid video id:", str(e))
        except Exception as e:
            print(type(e), str(e))
            if Arguments().debug:
                raise
        finally:
            return

    # Extractor
    if not os.path.exists(Arguments().output):
        print("\nThe specified directory does not exist.:{}\n".format(Arguments().output))
        return
    try:
        CLIExtractor().run()
    except CancelledError as e:
        print(str(e))
