import argparse

import os
import signal
import time
from json.decoder import JSONDecodeError
from pathlib import Path
from httpcore import ReadTimeout as HCReadTimeout, NetworkError as HCNetworkError
from .arguments import Arguments
from .progressbar import ProgressBar
from .. exceptions import InvalidVideoIdException, NoContents, PatternUnmatchError, UnknownConnectionError
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
    parser.add_argument(f'--{Arguments.Name.SAVE_ERROR_DATA}', action='store_true',
                        help='Save error data when error occurs(".dat" file)')
    parser.add_argument(f'--{Arguments.Name.VERSION}', action='store_true',
                        help='Show version')
    Arguments(parser.parse_args().__dict__)

    if Arguments().print_version:
        print(f'pytchat v{__version__}     © 2019 taizan-hokuto')
        return

    # Extractor
    if not Arguments().video_ids:
        parser.print_help()
        return
    for counter, video_id in enumerate(Arguments().video_ids):
        if '[' in video_id:
            video_id = video_id.replace('[', '').replace(']', '')
        if len(Arguments().video_ids) > 1:
            print(f"\n{'-' * 10} video:{counter + 1} of {len(Arguments().video_ids)} {'-' * 10}")

        try:
            video_id = extract_video_id(video_id)
            if not os.path.exists(Arguments().output):
                raise FileNotFoundError
            separated_path = str(Path(Arguments().output)) + os.path.sep
            path = util.checkpath(separated_path + video_id + '.html')
            err = None
            for _ in range(3):  # retry 3 times
                try:
                    info = VideoInfo(video_id)
                    break
                except (PatternUnmatchError, JSONDecodeError, InvalidVideoIdException) as e:
                    err = e
                    time.sleep(2)
                    continue
            else:
                print("Cannot parse video information.:{}".format(video_id))
                if Arguments().save_error_data:
                    util.save(err.doc, "ERR", ".dat")
                continue

            print(f"\n"
                  f" video_id: {video_id}\n"
                  f" channel:  {info.get_channel_name()}\n"
                  f" title:    {info.get_title()}")

            print(f" output path: {path}")
            duration = info.get_duration()
            pbar = ProgressBar(total=(duration * 1000), status="Extracting")
            ex = Extractor(video_id,
                    callback=pbar._disp,
                    div=10)
            signal.signal(signal.SIGINT, (lambda a, b: cancel(ex, pbar)))
            data = ex.extract()
            if data == []:
                return False
            pbar.reset("#", "=", total=len(data), status="Rendering  ")
            processor = HTMLArchiver(path, callback=pbar._disp)
            processor.process(
                [{'video_id': None,
                'timeout': 1,
                'chatdata': (action["replayChatItemAction"]["actions"][0] for action in data)}]
            )
            processor.finalize()
            pbar.reset('#', '#', status='Completed   ')
            pbar.close()
            print()
            if pbar.is_cancelled():
                print("\nThe extraction process has been discontinued.\n")
        except InvalidVideoIdException:
            print("Invalid Video ID or URL:", video_id)
        except NoContents as e:
            print(e)
        except FileNotFoundError:
            print("The specified directory does not exist.:{}".format(Arguments().output))
        except JSONDecodeError as e:
            print(e.msg)
            print("JSONDecodeError.:{}".format(video_id))
            if Arguments().save_error_data:
                util.save(e.doc, "ERR_JSON_DECODE", ".dat")
        except (UnknownConnectionError, HCNetworkError, HCReadTimeout) as e:
            print(f"An unknown network error occurred during the processing of [{video_id}]. : " + str(e))
        except PatternUnmatchError:
            print(f"PatternUnmatchError [{video_id}]. ")
        except Exception as e:
            print(type(e), str(e))

    return


def cancel(ex, pbar):
    ex.cancel()
    pbar.cancel()
