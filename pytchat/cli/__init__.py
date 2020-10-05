import argparse
import asyncio
try:
    from asyncio import CancelledError
except ImportError:
    from asyncio.futures import CancelledError
import os
import signal
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

    if not os.path.exists(Arguments().output):
        print("\nThe specified directory does not exist.:{}\n".format(Arguments().output))
        return
    try:
        Runner().run()
    except CancelledError as e:
        print(str(e))


class Runner:
    
    def run(self) -> None:
        ex = None
        pbar = None
        for counter, video_id in enumerate(Arguments().video_ids):
            if len(Arguments().video_ids) > 1:
                print(f"\n{'-' * 10} video:{counter + 1} of {len(Arguments().video_ids)} {'-' * 10}")

            try:
                video_id = extract_video_id(video_id)
                separated_path = str(Path(Arguments().output)) + os.path.sep
                path = util.checkpath(separated_path + video_id + '.html')
                try:
                    info = VideoInfo(video_id)
                except Exception as e:
                    print("Cannot parse video information.:{} {}".format(video_id, type(e)))
                    if Arguments().save_error_data:
                        util.save(str(e), "ERR", ".dat")
                    continue

                print(f"\n"
                    f" video_id: {video_id}\n"
                    f" channel:  {info.get_channel_name()}\n"
                    f" title:    {info.get_title()}\n"
                    f" output path: {path}")

                duration = info.get_duration()
                pbar = ProgressBar(total=(duration * 1000), status_txt="Extracting")
                ex = Extractor(video_id,
                        callback=pbar.disp,
                        div=10)
                signal.signal(signal.SIGINT, (lambda a, b: self.cancel(ex, pbar)))

                data = ex.extract()
                if data == []:
                    continue
                pbar.reset("#", "=", total=len(data), status_txt="Rendering  ")
                processor = HTMLArchiver(path, callback=pbar.disp)
                processor.process(
                    [{'video_id': None,
                    'timeout': 1,
                    'chatdata': (action["replayChatItemAction"]["actions"][0] for action in data)}]
                )
                processor.finalize()
                pbar.reset('#', '#', status_txt='Completed   ')
                pbar.close()
                print()
                if pbar.is_cancelled():
                    print("\nThe extraction process has been discontinued.\n")
            except InvalidVideoIdException:
                print("Invalid Video ID or URL:", video_id)
            except NoContents as e:
                print(f"Abort:{str(e)}:[{video_id}]")
            except (JSONDecodeError, PatternUnmatchError) as e:
                print("{}:{}".format(e.msg, video_id))
                if Arguments().save_error_data:
                    util.save(e.doc, "ERR_", ".dat")
            except (UnknownConnectionError, HCNetworkError, HCReadTimeout) as e:
                print(f"An unknown network error occurred during the processing of [{video_id}]. : " + str(e))
            except Exception as e:
                print(f"Abort:{str(type(e))} {str(e)[:80]}")
            finally:
                clear_tasks()

        return

    def cancel(self, ex=None, pbar=None) -> None:
        '''Called when keyboard interrupted has occurred.
        '''
        print("\nKeyboard interrupted.\n")
        if ex and pbar:
            ex.cancel()
            pbar.cancel()


def clear_tasks():
    '''
    Clear remained tasks.
    Called when internal exception has occurred or
    after each extraction process is completed.
    '''
    async def _shutdown():
        tasks = [t for t in asyncio.all_tasks()
                if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
            
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_shutdown())
    except Exception as e:
        print(e)
