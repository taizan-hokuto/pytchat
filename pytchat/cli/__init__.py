import argparse

import os
import sys
import signal
from json.decoder import JSONDecodeError
from pathlib import Path
from .arguments import Arguments
from .. exceptions import InvalidVideoIdException, NoContents, PatternUnmatchError
from .. processors.html_archiver import HTMLArchiver
from .. tool.extract.extractor import Extractor
from .. tool.videoinfo import VideoInfo
from .. util.extract_video_id import extract_video_id
from .. import util
from .. import __version__

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
    parser.add_argument(f'--{Arguments.Name.PBAR}', action='store_true',
                        help='Display rich progress bar')
    parser.add_argument(f'--{Arguments.Name.SAVE_ERROR_DATA}', action='store_true',
                        help='Save error data when error occurs(".dat" file)')
    parser.add_argument(f'--{Arguments.Name.VERSION}', action='store_true',
                        help='Show version')
    Arguments(parser.parse_args().__dict__)

    if Arguments().pbar:
        from .progressbar_rich import ProgressBar
    else:
        from .progressbar_simple import ProgressBar
    if Arguments().print_version:
        print(f'pytchat v{__version__}     © 2019 taizan-hokuto')
        return

    # Extractor
    if not Arguments().video_ids:
        parser.print_help()
        return
    for video_id in Arguments().video_ids:
        if '[' in video_id:
            video_id = video_id.replace('[', '').replace(']', '')
        try:
            video_id = extract_video_id(video_id)
            if os.path.exists(Arguments().output):
                path = Path(Arguments().output + video_id + '.html')
            else:
                raise FileNotFoundError
            info = VideoInfo(video_id)
            print(f"Extracting...\n"
                  f" video_id: {video_id}\n"
                  f" channel:  {info.get_channel_name()}\n"
                  f" title:    {info.get_title()}")

            print(f" output path: {path.resolve()}")
            duration = info.get_duration()
            pbar = ProgressBar(total=(duration * 1000), status="Extracting")
            ex = Extractor(video_id,                  
                    callback=pbar._disp,
                    div=10)
            signal.signal(signal.SIGINT, (lambda a, b: cancel(ex, pbar)))
            data = ex.extract()
            if data == []:
                return False
            if Arguments().pbar:
                pbar.reset("#", "=", total=len(data), status="Rendering  ")
            else:
                pbar.reset("=", "", total=len(data), status="Rendering  ")
            processor = HTMLArchiver(Arguments().output + video_id + '.html', callback=pbar._disp)
            processor.process(
                [{'video_id': None,
                'timeout': 1,
                'chatdata': (action["replayChatItemAction"]["actions"][0] for action in data)}]
            )
            processor.finalize()
            if Arguments().pbar:
                pbar.reset('#', '#', status='Completed   ')
                pbar.close()
            else:
                pbar.close()
                print("\nCompleted")
            
            print()
            if pbar.is_cancelled():
                print("\nThe extraction process has been discontinued.\n")
                return False
            return True

        except InvalidVideoIdException:
            print("Invalid Video ID or URL:", video_id)
        except NoContents as e:
            print(e)
        except FileNotFoundError:
            print("The specified directory does not exist.:{}".format(Arguments().output))
        except JSONDecodeError as e:
            print(e.msg)
            print("Cannot parse video information.:{}".format(video_id))
            if Arguments().save_error_data:
                util.save(e.doc, "ERR_JSON_DECODE", ".dat")
        except PatternUnmatchError as e:
            print(e.msg)
            print("Cannot parse video information.:{}".format(video_id))
            if Arguments().save_error_data:
                util.save(e.doc, "ERR_PATTERN_UNMATCH", ".dat")

    return


def cancel(ex, pbar):
    ex.cancel()
    pbar.cancel()
