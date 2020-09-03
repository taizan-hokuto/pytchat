import argparse

import os
import signal
from json.decoder import JSONDecodeError
from pathlib import Path
from .arguments import Arguments
from .progressbar import ProgressBar
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
    parser.add_argument(f'--{Arguments.Name.VERSION}', action='store_true',
                        help='Show version')
    parser.add_argument(f'--{Arguments.Name.SAVE_ERROR_DATA}', action='store_true',
                        help='Save error data when error occurs(".dat" file)')
    Arguments(parser.parse_args().__dict__)
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
            pbar = ProgressBar(duration)
            ex = Extractor(video_id,
                    processor=HTMLArchiver(Arguments().output + video_id + '.html'),
                    callback=pbar._disp,
                    div=10)
            signal.signal(signal.SIGINT, (lambda a, b: cancel(ex, pbar)))
            ex.extract()
            pbar.close()
            if pbar.is_cancelled():
                print("\nThe extraction process has been discontinued.\n")
                return
            print("\nThe extraction process has been completed.\n")
        except InvalidVideoIdException:
            print("Invalid Video ID or URL:", video_id)
        except (TypeError, NoContents) as e:

            print(e.with_traceback())
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


def cancel(ex: Extractor, pbar: ProgressBar):
    ex.cancel()
    pbar.cancel()
