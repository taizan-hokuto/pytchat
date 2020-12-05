import asyncio
import os
import signal
import traceback
from httpcore import ReadTimeout as HCReadTimeout, NetworkError as HCNetworkError
from json.decoder import JSONDecodeError
from pathlib import Path
from .arguments import Arguments
from .progressbar import ProgressBar
from .. import util
from .. exceptions import InvalidVideoIdException, NoContents, PatternUnmatchError, UnknownConnectionError
from .. processors.html_archiver import HTMLArchiver
from .. tool.extract.extractor import Extractor
from .. tool.videoinfo import VideoInfo


class CLIExtractor:

    def run(self) -> None:
        ex = None
        pbar = None
        for counter, video_id in enumerate(Arguments().video_ids):
            if len(Arguments().video_ids) > 1:
                print(f"\n{'-' * 10} video:{counter + 1} of {len(Arguments().video_ids)} {'-' * 10}")

            try:
                video_id = util.extract_video_id(video_id)
                separated_path = str(Path(Arguments().output)) + os.path.sep
                path = util.checkpath(separated_path + video_id + '.html')
                try:
                    info = VideoInfo(video_id)
                except (PatternUnmatchError, JSONDecodeError) as e:
                    print("Cannot parse video information.:{} {}".format(video_id, type(e)))
                    if Arguments().debug:
                        util.save(str(e.doc), "ERR", ".dat")
                    continue
                except Exception as e:
                    print("Cannot parse video information.:{} {}".format(video_id, type(e)))
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
                if data == [] or data is None:
                    continue
                pbar.reset("#", "=", total=1000, status_txt="Rendering  ")
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
                if Arguments().debug:
                    filename = util.save(e.doc, "ERR_", ".dat")
                    traceback.print_exc()
                    print(f"Saved error data: {filename}")
            except (UnknownConnectionError, HCNetworkError, HCReadTimeout) as e:
                if Arguments().debug:
                    traceback.print_exc()
                print(f"An unknown network error occurred during the processing of [{video_id}]. : " + str(e))
            except Exception as e:
                print(f"Abort:{str(type(e))} {str(e)[:80]}")
                if Arguments().debug:
                    traceback.print_exc()
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
        print(str(e))
        if Arguments().debug:
            traceback.print_exc()
